from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpRequest, JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils.timezone import localtime
from django.db.models import Min, Max
from monitoring.models import Machine, Machine_state, Job, Cycle, Monitor_operation
from monitoring.utils import is_ajax, machine_current_database_state
from monitoring.utils import convert_time_django_javascript, convert_to_local_time
from monitoring.utils import timedelta_to_HHMMSS, parse_isoformat
from monitoring.utils import update_machine, update_machine_state
from monitoring import strings
from datetime import timedelta, datetime
from collections import defaultdict

# Create your views here.
def home(request):
    machines = Machine.objects.all().exclude(name=strings.machine_uknown)
    virtual_machines = []
    if is_ajax(request):
        #call_counter = request.GET['calls_counter']
        machines_json = dict()
        for machine in machines:
            # saves state of the machine to a variable
            current_state = machine_current_database_state(machine)    # Get job data for the machine
            job_data = get_machine_job_data(machine)
            if job_data:
                current_state['active_job'] = job_data  # Add job data to the current state
            current_state = convert_time_django_javascript(current_state)
            machines_json[machine.name] = current_state
        return JsonResponse({'machines': machines_json}, status=200)
    elif not is_ajax(request):
        for machine in machines:
            # vm = current_machine_state(machine)
            # vm = machine_current_state(machine, call_counter, work_offline=work_offline)
            # vm['machine'] = machine
            virtual_machines.append(machine_current_database_state(machine))
    context = {
        'machines': machines,
        'virtual_machines': virtual_machines,
    }        
    return render(request, "monitoring/dashboard_main.html", context)

def proxy(request):
    if request.method == 'POST':
        try:
            post_data = request.POST
        except ValueError:
            pass  # Handle form data parsing error if necessary

        # get last machine state object and change it
        try:
            # get both states of machine current and previous
            machine = Machine.objects.filter(name=post_data['name']).get()
            # mark current_state as previous
            machine.switch_statuses()
            # change previous_state with POST data and mark it as current_state
            machine.current_state.set_state_from_POST(post_data)
            machine.log_status_change()
            # save both states
            machine.last_state.save()
            machine.current_state.save()
            
            # machine always has to be updated
            # the checking if the machine 
            # has changed status is done before the request is sent
            # do if machine has changed status
            machine.update_from_state()
            machine.save()
            machine.check_cycle()
            machine.save()
        except Exception as e:
            print(e)

    return JsonResponse({}, status=200)

# View for day activity logs
def day_activity(reqeust):
    return HttpResponse('')

def about(request):
    return HttpResponse('<h1>About</h1>')

# View for machine detail
def machine_detail(request, machine_id):
    machine = get_object_or_404(Machine, id=machine_id)
    job_list = Job.objects.filter(machine=machine).order_by('-started')
    
    # Pagination setup (10 jobs per page)
    paginator = Paginator(job_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'machine': machine,
        'page_obj': page_obj, # For paginated job list
    }

    return render(request, 'monitoring/machine_detail.html', context)

def job_detail(request, job_id):
    # Retrieve the job object by its ID or return a 404 error if not found
    job = get_object_or_404(Job, id=job_id)
    
    # Pass the job object to the context for rendering in the template
    context = {
        'job': job,
    }
    
    return render(request, 'monitoring/job_detail.html', context)

def get_job_productivity(request, pk):
    # Check if it is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        job = get_object_or_404(Job.objects.prefetch_related('cycle_set'), pk=pk)
        
        setup_time = job.setup_total_time
        changing_parts_time = job.part_changing_time
        machining_time = job.machining_time
        setup_time_correction = timedelta()

        cycles_by_day = defaultdict(list)

        # Calculate times based on whether the job is finished
        if not job.was_job_finished:
            # Aggregate times from all cycles
            for cycle in job.cycle_set.all():
                day = localtime(cycle.started).date()
                cycles_by_day[day].append(cycle)
                if cycle.is_full_cycle:
                    setup_time -= cycle.duration
                    setup_time -= cycle.changing_time
                    machining_time += cycle.duration
                    changing_parts_time += cycle.changing_time
            for day, cycles in cycles_by_day.items():
                start_of_day = cycles[0].started
                end_of_day = cycles[-1].ended
                if not end_of_day:
                    end_of_day = start_of_day
                
                setup_time_correction += (end_of_day - start_of_day)
            setup_time += setup_time_correction
            

        # Prepare the data dictionary to return as JSON
        data = {
            'setup_time': timedelta_to_HHMMSS(setup_time),
            'changing_parts_time': timedelta_to_HHMMSS(changing_parts_time),
            'machining_time': timedelta_to_HHMMSS(machining_time),
        }

        return JsonResponse(data)
    
    # If the request is not AJAX, handle it as needed
    return JsonResponse({'error': 'Invalid request'}, status=400)

def cycle_timeline(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    job_data = {
        'started': localtime(job.started).isoformat() if job.started else None,
        'ended': localtime(job.ended).isoformat() if job.ended else None,
        'setup_total_time': job.setup_total_time.total_seconds(),
        'setup_active_time': job.setup_active_time.total_seconds(),
        'setup_idle_time': job.setup_idle_time.total_seconds(),
    }

    mdi_cycles_data = []

    if job.was_job_finished:
        job = Job.objects.prefetch_related('archived_cycle_set').get(id=job_id)
        cycle_set = job.archived_cycle_set.all()
        cycle_type = 'archived'
        job_data['is_finished'] = True
    else:
        job = Job.objects.prefetch_related('cycle_set').get(id=job_id)
        cycle_set = job.cycle_set.all().order_by('-started')
        last_cycle = cycle_set.first()
        if last_cycle and last_cycle.ended:
            job_data['ended'] = localtime(last_cycle.ended).isoformat()
        elif last_cycle and not last_cycle.ended:
            last_cycle.ended = localtime(last_cycle.started + last_cycle.duration).isoformat()
            job_data['ended'] = last_cycle.ended
        cycle_type = 'active'
        job_data['is_finished'] = False

        mdi_cycles = Cycle.objects.filter(
            job=None,
            started__gte=job_data['started'],
            started__lte=job_data['ended']
        ).order_by('started')

        mdi_cycles_data = [{
            'started': localtime(cycle.started).isoformat(),
            'ended': localtime(cycle.ended).isoformat() if cycle.ended else localtime(cycle.started + cycle.duration).isoformat(),
            'duration': cycle.duration.total_seconds(),
            'changing_time': cycle.changing_time.total_seconds(),
            'is_setup': getattr(cycle, 'is_setting_cycle', False),
            'is_warmup': getattr(cycle, 'is_warm_up', False),
            'is_full_cycle': getattr(cycle, 'is_full_cycle', True),
            'id': cycle.id,
            'tool_sequence': cycle.tool_sequence,
            'is_mdi': True
        } for cycle in mdi_cycles]

    job_data['cycle_type'] = cycle_type

    earliest_full_cycle = None
    cycles_data = []

    for cycle in cycle_set:
        cycle_data = {
            'started': localtime(cycle.started).isoformat(),
            'ended': localtime(cycle.ended).isoformat() if cycle.ended else localtime(cycle.started + cycle.duration).isoformat(),
            'duration': cycle.duration.total_seconds(),
            'changing_time': cycle.changing_time.total_seconds(),
            'is_setup': getattr(cycle, 'is_setting_cycle', False),
            'is_warmup': getattr(cycle, 'is_warm_up', False),
            'is_full_cycle': getattr(cycle, 'is_full_cycle', True) if cycle_type == 'active' else True,
            'id': cycle.id,
            'tool_sequence': cycle.tool_sequence,
        }
        cycles_data.append(cycle_data)

        if cycle_data['is_full_cycle']:
            cycle_started = parse_isoformat(cycle_data['started'])
            if earliest_full_cycle is None or cycle_started < parse_isoformat(earliest_full_cycle['started']):
                earliest_full_cycle = cycle_data

    if earliest_full_cycle:
        initial_setup_time = {
            'started': job_data['started'],
            'ended': earliest_full_cycle['started'],
            'duration': (parse_isoformat(earliest_full_cycle['started']) - parse_isoformat(job_data['started'])).total_seconds()
        }
    else:
        initial_setup_time = {
            'started': job_data['started'],
            'ended': job_data['ended'],
            'duration': (parse_isoformat(job_data['ended']) - parse_isoformat(job_data['started'])).total_seconds()
        }

    return JsonResponse({
        'job': job_data,
        'cycles': cycles_data,
        'mdi_cycles': mdi_cycles_data,
        'initial_setup_time': initial_setup_time
    })

@require_POST
def finish_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if job.is_ready_to_finish:
        job.finished()  # Call the finished method to mark the job as finished
        job.save()
    return HttpResponseRedirect(reverse('job_detail', args=[job_id]))  # Redirect back to the job detail page

@require_POST
def unarchive_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if job.was_job_finished:
        job.unarchive()  # Call the unarchive method
        job.save()
    return HttpResponseRedirect(reverse('job_detail', args=[job_id]))  # Redirect back to the job detail page

# function to ge the job data for a machine
def get_machine_job_data(machine):

    # Retrieve the latest job for the machine
    try:
        job = Job.objects.filter(machine=machine).latest('started')  # assuming a relation to machine
    except Job.DoesNotExist:
        return None

    # Structure the job data into a dictionary
    job_data = {
        'project': job.project,
        'nc_program': job.nc_program,
        'currently_made_quantity': job.currently_made_quantity,
        'required_quantity': job.required_quantity,
        'operation': job.operation,
        'operations_total': job.operations_total,
        'started': convert_to_local_time(job.started).strftime("%Y-%m-%d %H:%M:%S") if job.started else None,
        'ended': convert_to_local_time(job.ended).strftime("%Y-%m-%d %H:%M:%S") if job.ended else None,
        'part_changing_time': str(job.part_changing_time),
        'cycle_time': str(job.cycle_time),
        'parts_per_cycle': job.parts_per_cycle,
        'will_end_at': convert_to_local_time(job.will_end_at).strftime("%Y-%m-%d %H:%M:%S") if job.will_end_at else None,
    }
    return job_data

# View to display the next job for each machine
def next_jobs_view(request):
    # Step 1: Filter machines that are not test machines
    machines = Machine.objects.filter(is_test_machine=False)

    # Step 2: Fetch all monitor operations
    operations = Monitor_operation.objects.all()

    # Step 3: Assign the highest-priority operation to each machine
    for machine in machines:
        # Find the highest-priority operation for this machine
        highest_priority_operation = operations.filter(machine=machine).order_by('priority').first()
        
        # Step 4: Dynamically add 'next_job' to the machine instance
        machine.next_job = highest_priority_operation

    # Step 5: Return the context with machines and their assigned jobs
    context = {
        'machines': machines,
    }

    return render(request, 'monitoring/next_jobs.html', context)

# View to check if the next jobs have changed
def check_next_jobs(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Get the raw data from POST request
        data = request.POST['data']  # This retrieves the JSON string

        # Parse the string into Python list of dictionaries
        data = eval(data)  # Safely parse the data (use eval here since it's sent as string)

        changed = False
        
        for pair in data:
            machine_pk = pair.get('machine_pk')
            job_pk = pair.get('job_pk')
            
            # Fetch the next job for the machine
            next_job = Monitor_operation.objects.filter(machine_id=machine_pk).order_by('priority').first()
            
            # Check if the job PK has changed
            if next_job and next_job.pk != int(job_pk):
                changed = True
                break
        
        return JsonResponse({'changed': changed})
    
    # If the request is not an AJAX request, redirect to the next jobs list
    return redirect('next_jobs')
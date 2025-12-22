from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils.timezone import localtime, now
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.db import transaction
from django.db.models import Min, Max
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from monitoring.models import Machine, Machine_state, Job, Cycle, Monitor_operation, MachineOperationAssignment
from monitoring.models import PushSubscription, MachineSubscription
from django.db.models import Q
from monitoring.defaults import machines_to_show, machines_to_hide
from monitoring.utils.utils import is_ajax, machine_current_database_state
from monitoring.utils.utils import convert_time_django_javascript, convert_to_local_time
from monitoring.utils.utils import timedelta_to_HHMMSS, parse_isoformat
from monitoring.utils.push_notifications import send_push_to_subscribers, send_push_to_raw_subscription
from monitoring import strings
from datetime import timedelta, datetime
from collections import defaultdict
import json
import os
import threading
import time

# Cache for machine states
machine_states_cache = {}

# Machine data - initialized lazily to avoid database queries at module import time
# This is required for Daphne/ASGI compatibility
machines_data = None
_machines_data_initialized = False

cache_lock = threading.Lock()


def get_machines_data():
    """
    Lazily initialize and return machines_data.
    This avoids database queries at module import time, which is required for Daphne/ASGI.
    """
    global machines_data, _machines_data_initialized

    if not _machines_data_initialized:
        with cache_lock:
            # Double-check inside lock
            if not _machines_data_initialized:
                machines_data = {
                    name: (machine, machine.current_state.id)
                    for name, machine in {
                        name: Machine.objects.get(id=id)
                        for name, id in machines_to_show.items()
                    }.items()
                    if machine.current_state
                }
                _machines_data_initialized = True

    return machines_data


def initialize_machine_states_cache():
    """
    Populate the machine_states_cache from machines_data with all information about the machine state.
    """
    global machine_states_cache

    data = get_machines_data()

    with cache_lock:  # Ensure thread-safe initialization
        # Iterate over machines_data and populate the cache
        for machine_name, (machine, state_id) in data.items():
            if machine.current_state:  # Ensure the machine has a current state
                machine_states_cache[machine_name] = {
                    "status": machine.current_state.status,
                    "this_cycle_duration": machine.current_state.this_cycle_duration,
                    "remain_time": machine.current_state.remain_time,
                    "last_cycle_duration": machine.current_state.last_cycle_duration,
                    "current_tool": machine.current_state.current_tool,
                    "active_nc_program": machine.current_state.active_nc_program,
                    "current_machine_time": machine.current_state.current_machine_time,
                }

# NOTE: Cache is initialized lazily on first request, not at module import
# This is required for Daphne/ASGI compatibility


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


def api_login_view(request):
    """
    🔐 API login endpoint.
    Accepts POST with username and password, authenticates user, and starts a session.
    Returns JSON with user info or error.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST method is allowed"}, status=405)

    username = request.POST.get("username")
    password = request.POST.get("password")

    if not username or not password:
        return JsonResponse({"success": False, "error": "Missing username or password"}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({
            "success": True,
            "username": user.username,
            "user_id": user.id,
            "is_staff": user.is_staff,
        })
    else:
        return JsonResponse({"success": False, "error": "Invalid credentials"}, status=403)


def api_logout_view(request):
    """
    🚪 API logout endpoint.
    Accepts POST and logs out the current user. Responds with success message.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST method is allowed"}, status=405)

    logout(request)
    return JsonResponse({"success": True, "message": "Logged out successfully"})


def get_webpush_public_key(request):
    """
    🔑 Returns the VAPID public key for use in client-side push subscription.
    Used by JavaScript before calling PushManager.subscribe().
    """
    return JsonResponse({"publicKey": settings.WEBPUSH_PUBLIC_KEY})


def service_worker(request):
    """
    🛠️ Serves the service-worker.js script from the static/js directory.
    This route is required for proper registration of service workers on some platforms.
    """
    js_path = os.path.join(settings.BASE_DIR, 'monitoring', 'static', 'js', 'service-worker.js')
    print("🛠️  Serving service-worker.js")  # or use logging.info()
    with open(js_path, "rb") as f:
        return HttpResponse(f.read(), content_type="application/javascript")


def dynamic_manifest(request, machine_id):
    """
    📱 Dynamically generates a manifest.json for a given machine ID.
    Used to enable PWA install on a per-machine subscription page.
    """
    machine = get_object_or_404(Machine, id=machine_id)

    manifest = {
        "name": f"Subscribe {machine.name}",
        "short_name": machine.name,
        "start_url": f"/monitoring/machine-subscribe/{machine.id}/",
        "display": "standalone",
        "background_color": "#1b2b68",
        "theme_color": "#1b2b68",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/static/icons/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/icons/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }

    return JsonResponse(manifest)


@csrf_exempt
@require_POST
def trigger_notification(request):
    """
    🧪 Manually triggers a push notification for testing purposes.
    Accepts a POST with machine name and event_type, builds a test payload,
    and sends notifications to subscribed users using `send_push_to_subscribers`.

    Note: Not called automatically by production machine state logic.
    """
    try:
        data = json.loads(request.body)
        machine_name = data.get("machine")
        event_type = data.get("event_type")
        extra_info = data.get("message", "")  # Optional custom message

        if not machine_name or not event_type:
            return JsonResponse({"error": "Missing machine or event_type"}, status=400)

        try:
            machine = Machine.objects.get(name=machine_name)
        except Machine.DoesNotExist:
            return JsonResponse({"error": f"Machine '{machine_name}' not found"}, status=404)

        # Define the message
        if event_type == "alarm":
            title = f"🚨 Alarm on {machine.name}"
            body = f"{machine.name} alarm {extra_info}" or f"Alarm on {machine.name}"
        elif event_type == "cycle_end":
            title = f"✅ Cycle Ended on {machine.name}"
            body = f"{machine.name} has finished a cycle."
        else:
            return JsonResponse({"error": f"Unsupported event_type: {event_type}"}, status=400)

        # Call the helper to send the notifications
        send_push_to_subscribers(machine, event_type, {
            "title": title,
            "body": body,
            "machine_id": machine.id
            })

        return JsonResponse({"status": "Notifications sent"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt  
@require_POST
@login_required
def save_subscription(request):
    """
    💾 Saves or updates a push subscription in the database.
    Associates it with the currently logged-in user. Required before linking to machine subscriptions.
    """
    try:
        data = json.loads(request.body)

        endpoint = data.get("endpoint")
        keys = data.get("keys", {})
        auth = keys.get("auth")
        public_key = keys.get("p256dh")
        user_agent = request.headers.get("User-Agent", "")

        if not endpoint or not auth or not public_key:
            return JsonResponse({"error": "Missing fields"}, status=400)

        # Either update existing or create new subscription
        subscription, created = PushSubscription.objects.update_or_create(
            user=request.user,
            endpoint=endpoint,
            defaults={
                "auth_key": auth,
                "public_key": public_key,
                "user_agent": user_agent,
                "is_active": True,
                "updated_at": now(),
            },
        )

        return JsonResponse({
            "status": "created" if created else "updated",
            "subscription_id": subscription.id
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_POST
@login_required
def unsubscribe(request):
    """
    ❌ Marks a push subscription as inactive based on endpoint.
    Used when the client unsubscribes completely (not per-machine).
    """
    try:
        data = json.loads(request.body)
        endpoint = data.get("endpoint")

        if not endpoint:
            return JsonResponse({"error": "Missing endpoint"}, status=400)

        # Try to find a matching subscription
        try:
            subscription = PushSubscription.objects.get(user=request.user, endpoint=endpoint)
        except PushSubscription.DoesNotExist:
            return JsonResponse({"status": "not found"}, status=404)

        if not subscription.is_active:
            return JsonResponse({"status": "already inactive"})

        # Soft-deactivate
        subscription.is_active = False
        subscription.save()

        return JsonResponse({"status": "unsubscribed"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
@login_required
def subscribe_machine(request):
    """
    🔔 Subscribes a user to a specific event (e.g., 'alarm') on a specific machine.
    Requires push subscription info and machine/event data.
    """
    try:
        data = json.loads(request.body)

        subscription_data = data.get("subscription", {})
        machine_name = data.get("machine")
        event_type = data.get("event_type")

        endpoint = subscription_data.get("endpoint")
        keys = subscription_data.get("keys", {})
        auth = keys.get("auth")
        public_key = keys.get("p256dh")
        user_agent = request.headers.get("User-Agent", "")

        if not endpoint or not auth or not public_key or not machine_name or not event_type:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Get or create PushSubscription
        subscription, _ = PushSubscription.objects.update_or_create(
            user=request.user,
            endpoint=endpoint,
            defaults={
                "auth_key": auth,
                "public_key": public_key,
                "user_agent": user_agent,
                "is_active": True,
                "updated_at": now(),
            }
        )

        # Get machine
        machine = Machine.objects.get(name=machine_name)

        # Create MachineSubscription
        ms, created = MachineSubscription.objects.get_or_create(
            subscription=subscription,
            machine=machine,
            event_type=event_type
        )

        return JsonResponse({"status": "subscribed", "created": created})

    except Machine.DoesNotExist:
        return JsonResponse({"error": "Machine not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
@login_required
def unsubscribe_machine(request):
    """
    📴 Removes a machine-event subscription for the current user.
    The base push subscription remains unless globally removed.
    """
    try:
        data = json.loads(request.body)

        subscription_data = data.get("subscription", {})
        machine_name = data.get("machine")
        event_type = data.get("event_type")

        endpoint = subscription_data.get("endpoint")

        if not endpoint or not machine_name or not event_type:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Try to find the user's subscription with the same endpoint
        try:
            subscription = PushSubscription.objects.get(user=request.user, endpoint=endpoint)
        except PushSubscription.DoesNotExist:
            return JsonResponse({"error": "Subscription not found"}, status=404)

        try:
            machine = Machine.objects.get(name=machine_name)
        except Machine.DoesNotExist:
            return JsonResponse({"error": "Machine not found"}, status=404)

        deleted, _ = MachineSubscription.objects.filter(
            subscription=subscription,
            machine=machine,
            event_type=event_type
        ).delete()

        return JsonResponse({"status": "unsubscribed", "deleted": deleted > 0})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def machine_subscribe_view(request, machine_id):
    """
    📄 Renders the subscription management page for a specific machine.
    Includes machine ID and name in the context.
    """
    if not request.user.is_authenticated:
        return redirect("login")  # Or your login URL
    
    machine = get_object_or_404(Machine, pk=machine_id)
    return render(request, "monitoring/machine_subscribe.html", {
        "machine_id": machine.id,
        "machine_name": machine.name
    })


@login_required
def my_subscriptions(request):
    """
    📦 Returns all active subscriptions and related machine-event mappings for the logged-in user.
    Used for account-wide subscription management or diagnostics.
    """
    # Get all active subscriptions for this user
    subscriptions = PushSubscription.objects.filter(user=request.user, is_active=True)

    # Preload related MachineSubscription rows
    machine_subs = MachineSubscription.objects.filter(subscription__in=subscriptions).select_related("machine", "subscription")

    # Format the results with endpoint info
    results = [
        {
            "machine": ms.machine.name,
            "event": ms.event_type,
            "endpoint": ms.subscription.endpoint
        }
        for ms in machine_subs
    ]

    return JsonResponse(results, safe=False)


@csrf_exempt
@require_POST
@login_required
def get_machine_subscriptions(request, machine_id):
    """
    ✅ API view that returns event types the user is subscribed to *on this device/browser*
    for a specific machine. Matches by endpoint and user.
    """

    try:
        data = json.loads(request.body)
        endpoint = data.get("endpoint")
        if not endpoint:
            return JsonResponse({"error": "Missing endpoint"}, status=400)

        machine = Machine.objects.get(id=machine_id)

        try:
            subscription = PushSubscription.objects.get(user=request.user, endpoint=endpoint, is_active=True)
        except PushSubscription.DoesNotExist:
            return JsonResponse({"machine_id": machine_id, "subscribed_events": []})

        subscriptions = MachineSubscription.objects.filter(
            machine=machine,
            subscription=subscription
        )

        event_types = [sub.event_type for sub in subscriptions]

        return JsonResponse({
            "machine_id": machine_id,
            "subscribed_events": event_types
        })

    except Machine.DoesNotExist:
        return JsonResponse({"error": "Machine not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def save_states_to_database():
    """
    Periodically save cached machine states to the database.
    """
    while True:
        with cache_lock:
            # Collect machines with updated states
            machines_to_update = []
            for machine_name, state in machine_states_cache.items():
                machine, _ = get_machines_data().get(machine_name, (None, None))
                if machine:
                    machine.current_state.status = state["status"]
                    machines_to_update.append(machine.current_state)

        # Bulk update the database outside the lock
        if machines_to_update:
            Machine_state.objects.bulk_update(machines_to_update, ["status", "active_nc_program"])

        time.sleep(3)  # Save every 3 seconds


@login_required
def dashboard(request):
    """
    Serve cached machine states to clients.
    """
    # Lazy initialization: populate cache on first request if empty
    if not machine_states_cache:
        initialize_machine_states_cache()

    if is_ajax(request):
        with cache_lock:
            return JsonResponse({"machines": machine_states_cache}, status=200)

    context = {"machines": get_machines_data().keys()}
    return render(request, "monitoring/dashboard.html", context)

@csrf_exempt
@require_POST
def update_machine_status(request):
    """
    Update the states of multiple machines in the machine_states_cache based on the incoming JSON request.
    """
    try:
        # Parse JSON data from the request
        data = json.loads(request.body)
        machines_data = data.get("machines", [])

        if not machines_data:
            return JsonResponse({"error": "No machines data provided."}, status=400)

        # Update the cache for each machine
        with cache_lock:
            for machine_data in machines_data:
                machine_name = machine_data.get("machine_name")
                new_status = machine_data.get("status")
                new_active_nc_program = machine_data.get("active_nc_program")

                # Ensure the machine exists in the cache
                if machine_name in machine_states_cache:
                    machine_states_cache[machine_name]["status"] = new_status
                    machine_states_cache[machine_name]["active_nc_program"] = new_active_nc_program

        return JsonResponse({"message": "Machine states updated in cache successfully."}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Start background thread for saving states to the database
thread = threading.Thread(target=save_states_to_database, daemon=True)
thread.start()

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
# Uses MachineOperationAssignment model for assigned operations
def next_jobs_view(request):
    # Step 1: Filter machines that are not test machines and prefetch assignments
    machines = Machine.objects.filter(is_test_machine=False)\
        .exclude(pk__in=machines_to_hide.values())\
        .select_related(
            'operation_assignment',
            'operation_assignment__next_operation',
        )

    # Step 2: Assign the next operation from assignment to each machine
    for machine in machines:
        assignment = getattr(machine, 'operation_assignment', None)

        if assignment and assignment.next_operation:
            # Use the assigned next operation
            machine.next_job = assignment.next_operation
        else:
            # No assignment, machine has no next job
            machine.next_job = None

    # Step 3: Return the context with machines and their assigned jobs
    context = {
        'machines': machines,
    }

    return render(request, 'monitoring/next_jobs.html', context)

# View to display the current job for each machine
# Supports both card view and table view (airport-style)
# Uses MachineOperationAssignment model for assigned operations
def current_jobs_view(request):
    machines = Machine.objects.filter(is_test_machine=False)\
        .exclude(pk__in=machines_to_hide.values())\
        .select_related(
            'operation_assignment',
            'operation_assignment__current_operation_1',
            'operation_assignment__current_operation_2',
            'operation_assignment__current_operation_3',
            'operation_assignment__monitor_assigned_operation',
        )

    for m in machines:
        assignment = getattr(m, 'operation_assignment', None)

        if assignment:
            # Get all current operations from the assignment
            current_ops = assignment.get_all_current_operations()

            # Filter out "No operation" placeholder operations
            real_ops = [op for op in current_ops if op.name != "No operation"]
        else:
            real_ops = []

        if not real_ops:
            # No real operations, machine is IDLE
            m.current_job = None
            m.current_jobs = []
            m.current_status = 'none'
            m.current_warning = None
            m.progress_percent = 0
        else:
            # Primary current job (for backward compatibility)
            m.current_job = real_ops[0]
            # All current jobs (for new views supporting multiple operations)
            m.current_jobs = real_ops
            m.current_status = 'ok'
            m.current_warning = (
                f"Multiple operations in progress ({len(real_ops)})"
                if len(real_ops) > 1 else None
            )
            # Calculate progress percentage for primary operation
            if m.current_job.quantity > 0:
                m.progress_percent = (m.current_job.currently_made_quantity / m.current_job.quantity) * 100
            else:
                m.progress_percent = 0

    return render(request, 'monitoring/current_jobs.html', {'machines': machines})

# View to check if the next jobs have changed
def check_next_jobs(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Get the raw data from POST request
        data = request.POST['data']  # This retrieves the JSON string

        # Parse the string into Pthon list of dictionaries
        data = json.loads(data)  

        changed = False
        
        for pair in data:
            machine_pk = pair.get('machine_pk')
            job_monitor_operation_id = pair.get('job_monitor_operation_id')
            
            # Use values_list to only fetch 'id' (the primary key of Monitor_operation) and 'machine_id'
            next_job = Monitor_operation.objects.filter(machine_id=machine_pk).order_by('priority').values_list('machine_id', 'monitor_operation_id').first()
            
            # Check if the job PK has changed
            if next_job and next_job[1] != int(job_monitor_operation_id):
                changed = True
                break
        
        return JsonResponse({'changed': changed})
    
    # If the request is not an AJAX request, redirect to the next jobs list
    return redirect('next_jobs')

# View to update next Monitor_operation (the operation planned to be next for this machine)
@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF protection for external apps, if needed
@login_required  # Require user authentication
def update_next_monitor_operation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))  # Parse JSON data from request body
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        machine_pk = data.get('machine_pk')
        if not machine_pk:
            return JsonResponse({'error': 'Machine PK is required'}, status=400)

        # Get the next monitor operation (not in progress, lowest priority) for the given machine
        monitor_operation = Monitor_operation.objects.filter(machine_id=machine_pk, is_in_progress=False).order_by('priority').first()

        if not monitor_operation:
            return JsonResponse({'error': 'Monitor operation not found'}, status=404)

        # List of allowed fields to update
        allowed_fields = [
            'monitor_operation_id',
            'name',
            'quantity',
            'material',
            'report_number',
            'planned_start_date',
            'planned_finish_date',
            'location',
            'priority',
            'drawing_image_base64',
            'is_setup',
            'currently_made_quantity',
            ]

        integer_fields = ['quantity', 'priority', 'currently_made_quantity']
        date_filelds = ['planned_start_date', 'planned_finish_date']
        boolean_fields = ['is_setup']


        # Loop over allowed fields and update only if present in the data
        for field in allowed_fields:
            if field in data:
                if field in integer_fields:
                    setattr(monitor_operation, field, int(data[field]))
                elif field in date_filelds:
                    posted_date = datetime.fromisoformat(data[field]).date()
                    setattr(monitor_operation, field, posted_date)
                elif field in boolean_fields:
                    setattr(monitor_operation, field, bool(data[field]))
                else:
                    setattr(monitor_operation, field, data[field])

        # Save changes
        monitor_operation.save()

        return JsonResponse({'message': 'Monitor operation updated successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# View to update current Monitor_operation (the operation currently in progress for this machine)
@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF protection for external apps, if needed
@login_required  # Require user authentication
def update_current_monitor_operation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))  # Parse JSON data from request body
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        machine_pk = data.get('machine_pk')
        if not machine_pk:
            return JsonResponse({'error': 'Machine PK is required'}, status=400)

        # Get the current monitor operation (in progress) for the given machine
        monitor_operation = Monitor_operation.objects.filter(machine_id=machine_pk, is_in_progress=True).first()

        if not monitor_operation:
            return JsonResponse({'error': 'Monitor operation not found'}, status=404)

        # List of allowed fields to update
        allowed_fields = [
            'monitor_operation_id',
            'name',
            'quantity',
            'material',
            'report_number',
            'planned_start_date',
            'planned_finish_date',
            'location',
            'priority',
            'drawing_image_base64',
            'is_setup',
            'currently_made_quantity',
            ]

        integer_fields = ['quantity', 'priority', 'currently_made_quantity']
        date_filelds = ['planned_start_date', 'planned_finish_date']
        boolean_fields = ['is_setup']


        # Loop over allowed fields and update only if present in the data
        for field in allowed_fields:
            if field in data:
                if field in integer_fields:
                    setattr(monitor_operation, field, int(data[field]))
                elif field in date_filelds:
                    posted_date = datetime.fromisoformat(data[field]).date()
                    setattr(monitor_operation, field, posted_date)
                elif field in boolean_fields:
                    setattr(monitor_operation, field, bool(data[field]))
                else:
                    setattr(monitor_operation, field, data[field])

        # Save changes
        monitor_operation.save()

        return JsonResponse({'message': 'Monitor operation updated successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Test views
# Notifictaions
# ==========================================================

# test view for push notifications on apple
def push_test_view(request):
    return render(request, "monitoring/push_test.html")


@csrf_exempt
def send_to_subscription(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)

        subscription_info = data.get("subscription")
        payload = data.get("payload")

        if not subscription_info or not payload:
            return JsonResponse({"error": "Missing subscription or payload"}, status=400)

        result = send_push_to_raw_subscription(subscription_info, payload)
        return JsonResponse(result, status=200 if result["status"] == "success" else 500)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

# =============================================================

# Mobile API Views
# =============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_dashboard(request):
    """
    📱 Mobile dashboard API endpoint.
    Returns simplified machine status data optimized for mobile devices.
    Uses the cached machine states for fast response without database queries.

    GET /monitoring/api/mobile/dashboard/

    Authentication: Token required (Authorization: Token <token>)

    Response Format:
    {
        "machines": [
            {
                "id": 1,
                "name": "Machine_A",
                "status": "Running",
                "active_program": "O12345",
                "current_tool": "T05"
            },
            ...
        ],
        "timestamp": "2025-01-16T10:30:00Z"
    }

    Query Parameters:
    - exclude_virtual: true/false (default: false) - exclude virtual machines
    - exclude_test: true/false (default: true) - exclude test machines
    """
    # Get query parameters
    exclude_virtual = request.GET.get('exclude_virtual', 'false').lower() == 'true'
    exclude_test = request.GET.get('exclude_test', 'true').lower() == 'true'

    # Lazy initialization: populate cache on first request if empty
    if not machine_states_cache:
        initialize_machine_states_cache()

    # Build response data from cached machine states
    machines_list = []

    with cache_lock:
        # Iterate through machines_data which contains (machine, state_id) tuples
        for machine_name, (machine, state_id) in get_machines_data().items():
            # Skip machines based on filters
            if exclude_test and machine.is_test_machine:
                continue
            if exclude_virtual and machine.is_virtual_machine:
                continue

            # Get cached state for this machine
            cached_state = machine_states_cache.get(machine_name, {})

            # Build machine info from cache with fallbacks
            machine_info = {
                "id": machine.id,
                "name": machine_name,
                "status": cached_state.get("status", "Unknown"),
                "active_program": cached_state.get("active_nc_program", None),
                "current_tool": cached_state.get("current_tool", None),
            }

            machines_list.append(machine_info)

    # Return response with timestamp
    response_data = {
        "machines": machines_list,
        "timestamp": now().isoformat()
    }

    return JsonResponse(response_data, status=200)

# =============================================================

# Machine Operation Assignment API Endpoints
# =============================================================

@csrf_exempt
@require_POST
def sync_operation_pool(request):
    """
    Sync operation pool from Monitor G5.
    Receives daily catalog of available operations.

    POST /monitoring/api/sync-operation-pool/

    Request Body:
    {
        "operations": [
            {
                "monitor_operation_id": "OP-001",
                "report_id": "REP-001",
                "part_name": "Part A",
                "quantity": 100
            },
            ...
        ]
    }

    Logic:
    1. Create/update operations in the pool
    2. Delete operations NOT in the new pool, EXCEPT those currently assigned
    3. Mark all received operations as is_in_pool=True
    """
    try:
        data = json.loads(request.body)
        operations_data = data.get('operations', [])

        if not operations_data:
            return JsonResponse({'error': 'No operations provided'}, status=400)

        # Get IDs of operations that are currently assigned (should not be deleted)
        assigned_operation_ids = set()
        for assignment in MachineOperationAssignment.objects.all():
            if assignment.current_operation_1:
                assigned_operation_ids.add(assignment.current_operation_1.pk)
            if assignment.current_operation_2:
                assigned_operation_ids.add(assignment.current_operation_2.pk)
            if assignment.current_operation_3:
                assigned_operation_ids.add(assignment.current_operation_3.pk)
            if assignment.next_operation:
                assigned_operation_ids.add(assignment.next_operation.pk)
            if assignment.monitor_assigned_operation:
                assigned_operation_ids.add(assignment.monitor_assigned_operation.pk)

        # Track which monitor_operation_ids we received
        received_monitor_ids = set()
        created_count = 0
        updated_count = 0

        for op_data in operations_data:
            monitor_op_id = op_data.get('monitor_operation_id')
            if not monitor_op_id:
                continue

            received_monitor_ids.add(monitor_op_id)

            # Create or update operation
            operation, created = Monitor_operation.objects.update_or_create(
                monitor_operation_id=monitor_op_id,
                defaults={
                    'name': op_data.get('part_name', ''),
                    'report_number': op_data.get('report_id', ''),
                    'quantity': op_data.get('quantity', 0),
                    'is_in_pool': True,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        # Mark operations not in pool (but don't delete if assigned)
        operations_to_remove = Monitor_operation.objects.filter(
            is_in_pool=True
        ).exclude(
            monitor_operation_id__in=received_monitor_ids
        ).exclude(
            pk__in=assigned_operation_ids
        )

        # Mark as not in pool instead of deleting
        removed_count = operations_to_remove.update(is_in_pool=False)

        return JsonResponse({
            'success': True,
            'created': created_count,
            'updated': updated_count,
            'removed_from_pool': removed_count
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def monitor_assign_operation(request):
    """
    Monitor assigns operation to machine (current_operation_1 only).
    When Monitor changes its assignment, it overrides any manual override.

    POST /monitoring/api/monitor-assign-operation/

    Request Body:
    {
        "machine_pk": 1,
        "monitor_operation_id": "OP-001"
    }
    """
    try:
        data = json.loads(request.body)
        machine_pk = data.get('machine_pk')
        monitor_operation_id = data.get('monitor_operation_id')

        if not machine_pk:
            return JsonResponse({'error': 'machine_pk is required'}, status=400)

        # Get the machine
        try:
            machine = Machine.objects.get(pk=machine_pk)
        except Machine.DoesNotExist:
            return JsonResponse({'error': 'Machine not found'}, status=404)

        # Get the operation (if provided)
        operation = None
        if monitor_operation_id:
            try:
                operation = Monitor_operation.objects.get(monitor_operation_id=monitor_operation_id)
            except Monitor_operation.DoesNotExist:
                return JsonResponse({'error': 'Operation not found'}, status=404)

        # Get or create assignment
        assignment, created = MachineOperationAssignment.objects.get_or_create(
            machine=machine
        )

        # Check if Monitor assignment changed
        monitor_changed = (assignment.monitor_assigned_operation != operation)

        if monitor_changed:
            # Monitor changed - update current_operation_1 and clear manual override flag
            assignment.current_operation_1 = operation
            assignment.is_manually_overridden = False
            assignment.current_1_source = 'monitor'

        # Always update what Monitor assigned
        assignment.monitor_assigned_operation = operation
        assignment.monitor_last_updated = now()
        assignment.save()

        return JsonResponse({
            'success': True,
            'machine': machine.name,
            'operation': operation.name if operation else None,
            'monitor_changed': monitor_changed
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def manual_assign_operation(request):
    """
    Admin manually assigns operations to any slot.

    POST /monitoring/api/manual-assign-operation/

    Request Body:
    {
        "machine_pk": 1,
        "slot": "current_1",  // or "current_2", "current_3", "next"
        "operation_id": 123   // Monitor_operation PK, or null to clear
    }
    """
    try:
        data = json.loads(request.body)
        machine_pk = data.get('machine_pk')
        slot = data.get('slot')
        operation_id = data.get('operation_id')  # Can be null to clear

        if not machine_pk:
            return JsonResponse({'error': 'machine_pk is required'}, status=400)

        if slot not in ['current_1', 'current_2', 'current_3', 'next']:
            return JsonResponse({'error': 'Invalid slot. Use: current_1, current_2, current_3, or next'}, status=400)

        # Get the machine
        try:
            machine = Machine.objects.get(pk=machine_pk)
        except Machine.DoesNotExist:
            return JsonResponse({'error': 'Machine not found'}, status=404)

        # Get the operation (if provided)
        operation = None
        if operation_id:
            try:
                operation = Monitor_operation.objects.get(pk=operation_id)
            except Monitor_operation.DoesNotExist:
                return JsonResponse({'error': 'Operation not found'}, status=404)

        # Get or create assignment
        assignment, created = MachineOperationAssignment.objects.get_or_create(
            machine=machine
        )

        # Update the appropriate slot
        slot_field_map = {
            'current_1': 'current_operation_1',
            'current_2': 'current_operation_2',
            'current_3': 'current_operation_3',
            'next': 'next_operation',
        }

        setattr(assignment, slot_field_map[slot], operation)

        # Track manual override
        if slot == 'current_1':
            assignment.current_1_source = 'manual'
            assignment.is_manually_overridden = True

        assignment.manual_override_at = now()
        assignment.manual_override_by = request.user
        assignment.save()

        return JsonResponse({
            'success': True,
            'machine': machine.name,
            'slot': slot,
            'operation': operation.name if operation else None
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def toggle_operation_status(request):
    """
    Toggle operation status between setup and in progress.

    POST /monitoring/api/toggle-operation-status/

    Request Body:
    {
        "operation_id": 123,
        "is_setup": true  // true for setup, false for in progress
    }
    """
    try:
        data = json.loads(request.body)
        operation_id = data.get('operation_id')
        is_setup = data.get('is_setup')

        if operation_id is None:
            return JsonResponse({'error': 'operation_id is required'}, status=400)

        if is_setup is None:
            return JsonResponse({'error': 'is_setup is required'}, status=400)

        # Get the operation
        try:
            operation = Monitor_operation.objects.get(pk=operation_id)
        except Monitor_operation.DoesNotExist:
            return JsonResponse({'error': 'Operation not found'}, status=404)

        # Update status
        operation.is_setup = bool(is_setup)
        operation.save()

        return JsonResponse({
            'success': True,
            'operation_id': operation.id,
            'operation_name': operation.name,
            'is_setup': operation.is_setup
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ========================================
# Drawing Monitor API
# ========================================

@login_required
@require_POST
def set_drawing_cursor(request):
    """
    Set the cursor to a specific operation for drawing display.
    Activates cursor and broadcasts to drawing monitors via WebSocket.

    POST /monitoring/api/drawing/set-cursor/

    Request Body:
    {
        "operation_id": 123  // or null to deactivate
    }
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from .cursor_cache import set_cursor, deactivate_cursor
    import time

    try:
        data = json.loads(request.body)
        operation_id = data.get('operation_id')

        if operation_id is None:
            # Deactivate cursor
            deactivate_cursor()
            return JsonResponse({
                'success': True,
                'message': 'Cursor deactivated'
            })

        # Validate operation exists
        try:
            operation = Monitor_operation.objects.get(pk=operation_id)
        except Monitor_operation.DoesNotExist:
            return JsonResponse({'error': 'Operation not found'}, status=404)

        # Update cursor cache
        cursor_state = set_cursor(operation_id)

        # Broadcast to drawing monitors via WebSocket (no image - cached on client)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'drawing_updates',
            {
                'type': 'drawing_update',
                'operation_id': operation.id,
                'operation_name': operation.name,
                'timestamp': int(time.time())
            }
        )

        return JsonResponse({
            'success': True,
            'operation_id': operation.id,
            'operation_name': operation.name,
            'cursor_state': cursor_state
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_cursor_status(request):
    """
    Get current cursor status (for drawing monitor polling).

    GET /monitoring/api/drawing/cursor-status/

    Returns:
    {
        "is_active": true/false,
        "operation_id": 123,
        "last_activity": "2025-12-21T10:30:00",
        "seconds_since_activity": 5
    }
    """
    from .cursor_cache import get_active_cursor

    cursor_data = get_active_cursor()
    return JsonResponse(cursor_data)


def get_all_drawings(request):
    """
    Return all operations with their drawings for client-side caching.
    Preloads all drawings so WebSocket only needs to send operation_id.

    GET /monitoring/api/drawing/all/

    Response:
    {
        "drawings": {
            "123": {"name": "Part A", "drawing_base64": "data:image/..."},
            "456": {"name": "Part B", "drawing_base64": "data:image/..."}
        }
    }
    """
    operations = Monitor_operation.objects.filter(
        drawing_image_base64__isnull=False
    ).exclude(drawing_image_base64='')

    drawings = {}
    for op in operations:
        drawings[str(op.id)] = {
            'name': op.name,
            'drawing_base64': op.drawing_image_base64
        }

    return JsonResponse({'drawings': drawings})


@login_required
def get_available_operations(request):
    """
    Get list of operations available for assignment (for admin UI).

    GET /monitoring/api/available-operations/

    Query Params:
    - search: keyword to search in name, report_number, monitor_operation_id
    - limit: max number of results (default 50)

    Response:
    {
        "operations": [
            {
                "id": 123,
                "monitor_operation_id": "OP-001",
                "name": "Part A",
                "report_number": "REP-001",
                "quantity": 100
            },
            ...
        ]
    }
    """
    search = request.GET.get('search', '').strip()
    limit = int(request.GET.get('limit', 50))

    # Base query - only operations in the pool
    operations = Monitor_operation.objects.filter(is_in_pool=True)

    # Apply search filter
    if search:
        operations = operations.filter(
            Q(name__icontains=search) |
            Q(report_number__icontains=search) |
            Q(monitor_operation_id__icontains=search)
        )

    # Limit results
    operations = operations[:limit]

    # Build response
    operations_list = [
        {
            'id': op.id,
            'monitor_operation_id': op.monitor_operation_id,
            'name': op.name,
            'report_number': op.report_number,
            'quantity': op.quantity,
            'material': op.material,
        }
        for op in operations
    ]

    return JsonResponse({'operations': operations_list})


@login_required
def get_machine_assignments(request, machine_id):
    """
    Get current assignments for a machine.

    GET /monitoring/api/machine-assignments/<machine_id>/

    Response:
    {
        "machine": "VF2SSYT",
        "current_1": {...operation data...},
        "current_2": {...operation data...},
        "current_3": null,
        "next": {...operation data...},
        "is_manually_overridden": false,
        "current_1_source": "monitor"
    }
    """
    try:
        machine = Machine.objects.get(pk=machine_id)
    except Machine.DoesNotExist:
        return JsonResponse({'error': 'Machine not found'}, status=404)

    try:
        assignment = machine.operation_assignment
    except MachineOperationAssignment.DoesNotExist:
        # No assignment exists yet
        return JsonResponse({
            'machine': machine.name,
            'current_1': None,
            'current_2': None,
            'current_3': None,
            'next': None,
            'is_manually_overridden': False,
            'current_1_source': 'monitor'
        })

    def operation_to_dict(op):
        if op is None:
            return None
        return {
            'id': op.id,
            'monitor_operation_id': op.monitor_operation_id,
            'name': op.name,
            'report_number': op.report_number,
            'quantity': op.quantity,
            'currently_made_quantity': op.currently_made_quantity,
            'material': op.material,
        }

    return JsonResponse({
        'machine': machine.name,
        'current_1': operation_to_dict(assignment.effective_current_1),
        'current_2': operation_to_dict(assignment.current_operation_2),
        'current_3': operation_to_dict(assignment.current_operation_3),
        'next': operation_to_dict(assignment.next_operation),
        'is_manually_overridden': assignment.is_manually_overridden,
        'current_1_source': assignment.current_1_source
    })

# =============================================================

# Planning Interface Views (Admin)
# =============================================================

@login_required
def planning_grid(request):
    """
    Display grid of machines for planning operations.
    Mobile-optimized view showing all machines as clickable buttons.

    GET /monitoring/planning/
    """
    machines = Machine.objects.filter(is_test_machine=False)\
        .exclude(pk__in=machines_to_hide.values())\
        .select_related(
            'operation_assignment',
            'operation_assignment__current_operation_1',
            'operation_assignment__current_operation_2',
            'operation_assignment__current_operation_3',
            'operation_assignment__next_operation',
        )\
        .order_by('name')

    # Add assignment info to each machine for display
    for machine in machines:
        assignment = getattr(machine, 'operation_assignment', None)
        if assignment:
            machine.has_assignment = True
            # Count non-null current operations
            current_ops = [
                assignment.effective_current_1,
                assignment.current_operation_2,
                assignment.current_operation_3
            ]
            machine.current_op_count = sum(1 for op in current_ops if op is not None)
            machine.has_next_op = assignment.next_operation is not None
        else:
            machine.has_assignment = False
            machine.current_op_count = 0
            machine.has_next_op = False

    return render(request, 'monitoring/planning_grid.html', {'machines': machines})


@login_required
def planning_detail(request, machine_id):
    """
    Display planning detail page for a specific machine.
    Allows assigning operations to current and next slots.

    GET /monitoring/planning/<machine_id>/
    """
    machine = get_object_or_404(Machine, pk=machine_id)

    # Get or create assignment for this machine
    assignment = getattr(machine, 'operation_assignment', None)

    return render(request, 'monitoring/planning_detail.html', {
        'machine': machine,
        'assignment': assignment
    })


def drawing_monitor(request):
    """
    Full-screen drawing display monitor.
    Shows company logo when idle, operation drawing when cursor active.

    GET /monitoring/drawing-monitor/
    """
    return render(request, 'monitoring/drawing_monitor.html')


@login_required
def cursor_test(request):
    """
    Test page for cursor control.
    Use PgUp/PgDown to move cursor through operations.

    GET /monitoring/cursor-test/
    """
    operations = Monitor_operation.objects.filter(
        drawing_image_base64__isnull=False
    ).exclude(drawing_image_base64='').order_by('id')

    return render(request, 'monitoring/cursor_test.html', {
        'operations': operations
    })


# =============================================================
from django.db import models, transaction
import socket
import pytz
from statistics import median
from os import path
from math import ceil
from collections import Counter
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime, timedelta, date
from monitoring.utils import when_work_will_end, normalize_tool_sequence, timedelta_from_string, round_to_seconds
from monitoring import strings, defaults, testing_variables_defaut

# Model of a job
class Job(models.Model):
    # is defined by what project(part) has to be made on which machine
    # and how many parts should be produced
    # job might contain one or several operations
    project = models.CharField(max_length=25, default=defaults.job_project_default)
    nc_program = models.CharField(max_length=25, default=defaults.job_nc_program_defautl)
    currently_made_quantity = models.IntegerField(default=0)
    full_cycle = models.ForeignKey('monitoring.Cycle', on_delete=models.SET_DEFAULT, related_name='full_cycle', default=None, blank=True, null=True)
    required_quantity = models.IntegerField(default=0)
    operation =  models.IntegerField(null=True, blank=True)
    operations_total =  models.IntegerField(null=True, blank=True)
    started = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    ended = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    part_changing_time = models.DurationField(default=defaults.duration_one_minute)
    setup_total_time = models.DurationField(default=defaults.duration_zero)
    setup_active_time = models.DurationField(default=defaults.duration_zero)
    setup_idle_time = models.DurationField(default=defaults.duration_zero)
    machining_time = models.DurationField(default=defaults.duration_zero)
    cycle_time = models.DurationField(default=defaults.duration_one_minute)
    parts_per_cycle = models.IntegerField(default=1)
    will_end_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    is_finished = models.BooleanField(default=False)

    
    class Meta:
        ordering = ['started']

    # Method to get default job 
    @classmethod
    def get_default_pk(cls):
        job, created = cls.objects.get_or_create(
            project = 'Unknown',                
            currently_made_quantity = 0,
            required_quantity = 1,
            operation = 1,
            started = '2022-01-03 07:00:00',
            ended = '2022-01-07 16:00:00',
        )
        return job.pk

    def __str__(self):
        shown_name = self.project if self.project != defaults.job_project_default else self.nc_program
        time = self.started.strftime('%Y-%m-%d %H:%M')
        if self.required_quantity > 1:
            return_string = f'{shown_name}: {self.required_quantity} pcs | started: {time}'
        elif self.required_quantity <= 1:
            return_string = f'{shown_name}: {self.required_quantity} pc | started: {time}'
        return return_string

    def get_ended(self):
        all_cycles = Cycle.objects.all().filter(job=self)
        median_cycle_time = round_to_seconds(self.cycle_time)
        median_changing_time = round_to_seconds(self.part_changing_time)
        self.cycle_time = median_cycle_time
        self.part_changing_time = median_changing_time
        remain_parts = (self.required_quantity - self.currently_made_quantity) if (self.required_quantity - self.currently_made_quantity) > 0 else 0
        total_producing_time = (median_cycle_time + median_changing_time) * remain_parts
        #print(f'Cycle time: {median_cycle_time}, remain parts: {remain_parts} will be finished on {total_producing_time}')
        time_from_machine = datetime.now()
        if len(all_cycles) > 0:
            time_from_machine = all_cycles[0].machine.current_machine_time
            mod_time = time_from_machine.replace(tzinfo=pytz.timezone('Europe/Stockholm'))
            time_from_machine = mod_time
        work_will_end_at = when_work_will_end(time_from_machine, total_producing_time)
        self.will_end_at = work_will_end_at


    def get_cycle_time(self, all_cycles=None) -> timedelta:
        if all_cycles is None:
            all_cycles = Cycle.objects.all().filter(job=self)
        if len(all_cycles) > 0:
            cycle_time = median(map(lambda o: o.duration, all_cycles))
        else:
            cycle_time = timedelta(0)
        return round_to_seconds(cycle_time)

    def get_changing_time(self, all_cycles=None) -> timedelta:
        if all_cycles is None:
            all_cycles = Cycle.objects.all().filter(job=self)
        if len(all_cycles) > 0:
            changing_time = median(map(lambda o: o.changing_time, all_cycles))
        else:
            changing_time = defaults.duration_zero
        # check if changing time is not too large
        if changing_time > defaults.duration_one_hour:
            changing_time = defaults.duration_one_hour
        return round_to_seconds(changing_time)

    # Method to add one cycle
    def add_one_cycle(self):
        self.currently_made_quantity += self.parts_per_cycle

    # Method to find and set full cycle
    def find_full_cycle(self, double_tool=False):
        # Get all cycles associated with the job
        all_job_cycles = Cycle.objects.filter(job=self).order_by('started')

        previous_full_cycle = self.full_cycle

        # Check if there are three or fewer cycles, if so return None
        if len(all_job_cycles) <= 3:
            return None

        # Creating a list of tool sequences (as lists of integers)
        tool_sequences = [list(map(int, cycle.tool_sequence.split(','))) for cycle in all_job_cycles if cycle.tool_sequence]

        # Counting the frequency of each unique tool sequence
        sequence_counts = Counter(tuple(sequence) for sequence in tool_sequences)

        if not sequence_counts:
            return None

        # Determining the most common sequence
        most_common_sequence, _ = sequence_counts.most_common(1)[0]

        # Finding and returning the first cycle that has the most common sequence
        for cycle in all_job_cycles:
            if cycle.tool_sequence == '' or cycle.tool_sequence is None:
                continue
            if tuple(map(int, cycle.tool_sequence.split(','))) == most_common_sequence:
                # set cycle as full cycle
                self.full_cycle = cycle
                # check job's made quantity for first full cycle, compensate for first three cycles
                if self.currently_made_quantity == 0:
                    compensation = sequence_counts[most_common_sequence]
                    self.currently_made_quantity = self.parts_per_cycle * compensation
                    # write full_cycle = True and is_setting_cycle = False to all previous full cycles
                    most_common_sequence_str = ','.join(map(str, most_common_sequence))
                    # Normalize the most common sequence for comparison
                    normalized_most_common = normalize_tool_sequence(most_common_sequence_str, double_tool)
                    all_previous_full_cycles = [cycle for cycle in all_job_cycles if normalize_tool_sequence(cycle.tool_sequence, double_tool) == normalized_most_common]
                    for cycle in all_previous_full_cycles:
                        cycle.is_full_cycle = True
                        cycle.is_setting_cycle = False
                        cycle.save()
                # check if the full cycle has changed and adjust quantities accordingly
                if previous_full_cycle and cycle:
                    if previous_full_cycle != cycle:
                        self.compare_full_cycle(previous_full_cycle)
                return cycle
            

        return None  # Return None if no cycle meets the criteria
    
    # Method to compare and adjust quantities if full cycle has changed
    def compare_full_cycle(self, previous_full_cycle):
        is_tool_sequence_changed = False
        if previous_full_cycle.tool_sequence != self.full_cycle.tool_sequence:
            is_tool_sequence_changed = True
        if is_tool_sequence_changed:
            all_previous_full_cycles = Cycle.objects.filter(job=self, tool_sequence=previous_full_cycle.tool_sequence)
            # remove full_cycle = True from all previous full cycles
            for cycle in all_previous_full_cycles:
                cycle.is_full_cycle = False
                cycle.is_setting_cycle = True
                cycle.save()
            quantity_difference = self.parts_per_cycle * len(all_previous_full_cycles)
            self.currently_made_quantity -= quantity_difference
            if self.currently_made_quantity < 0:
                self.currently_made_quantity = 0
    
    # Method to compare cycle to full cycle
    # set is_full_cycle to True and is_setting_cycle to False if cycle is full cycle
    def compare_to_full_cycle(self, cycle):
        if self.full_cycle is None:
            return False
        if self.full_cycle.tool_sequence == cycle.tool_sequence:
            cycle.is_full_cycle = True
            cycle.is_setting_cycle = False
            return True
        return False
    
    # Method to check for broken cycle
    # if current cycle is and previous cycle combined are equal to full cycle
    def check_for_broken_cycle(self, cycle):
        if self.full_cycle is None:
            return False
        if cycle.is_warm_up:
            return False
        full_cycle_sequence = normalize_tool_sequence(self.full_cycle.tool_sequence)
        current_sequence = normalize_tool_sequence(cycle.tool_sequence)
        # Get all cycles associated with the job
        last_cycle = Cycle.objects.filter(job=self).order_by('-started')[1]
        # check if last cycle is warm up cycle and get previous cycle if it is
        if last_cycle.is_warm_up:
            last_cycle = Cycle.objects.filter(job=self).order_by('-started')[2]
        previous_sequence = normalize_tool_sequence(last_cycle.tool_sequence)
        if previous_sequence == full_cycle_sequence:
            return False
        resulte_sequence = previous_sequence + ',' + current_sequence 
        if resulte_sequence == full_cycle_sequence:
            cycle.is_setting_cycle = False
            last_cycle.is_setting_cycle = False
            cycle.save()
            last_cycle.save()
            return True

    # Method to check if job is finished
    def is_finished(self):
        if self.currently_made_quantity >= self.required_quantity and self.required_quantity !=0:
            return True
        return False

    # Method to do when job is finished
    def finished(self):
        cycles = Cycle.objects.filter(job=self)
        mdi_cycles = Cycle.objects.filter(started__gte=self.started, started__lte=self.ended, job=None)
        setup_cycles = []
        warm_up_cycles = []
        setup_time = defaults.duration_zero
        idle_time = defaults.duration_zero
        machining_time = defaults.duration_zero
        unrelated_machining_time = defaults.duration_zero  # includes warm up cycles

        for cycle in cycles:
            if cycle.is_setting_cycle and cycle.mode == strings.mode_auto:
                setup_time += cycle.duration
                setup_time += cycle.changing_time
                setup_cycles.append(cycle)
            elif cycle.is_warm_up:
                unrelated_machining_time += cycle.duration
                idle_time += cycle.changing_time
                warm_up_cycles.append(cycle)
            elif cycle.is_full_cycle:
                machining_time += cycle.duration
                machining_time += cycle.changing_time
            else:
                print(f'Not described case: {cycle}')
                setup_time += cycle.duration
                setup_time += cycle.changing_time
                setup_cycles.append(cycle)

        # Optimized deletion of setup cycles
        setup_cycle_ids = [cycle.id for cycle in setup_cycles]
        cycles.filter(id__in=setup_cycle_ids).delete()

        warm_up_cycles_ids = [cycle.id for cycle in warm_up_cycles]
        cycles.filter(id__in=warm_up_cycles_ids).delete()


        # Calculate additional times for MDI cycles and delete them efficiently
        mdi_cycle_ids = [cycle.id for cycle in mdi_cycles if cycle.job is None]
        for cycle in mdi_cycles.filter(id__in=mdi_cycle_ids):
            setup_time += cycle.duration
            setup_time += cycle.changing_time
        mdi_cycles.filter(id__in=mdi_cycle_ids).delete()

        # Archiving and deleting full cycles
        full_cycles = cycles.filter(is_full_cycle=True)
        archived_cycles = []
        for cycle in full_cycles:
            archived_cycle = Archived_cycle()  # Create a new instance
            archived_cycle.copy_from_cycle(cycle)  # Populate and get the instance back
            archived_cycles.append(archived_cycle)  # Append the populated instance to the list
        
        self.full_cycle = None

        with transaction.atomic():
            Archived_cycle.objects.bulk_create(archived_cycles)
            full_cycles.delete()
        
        self.setup_active_time += setup_time
        self.setup_idle_time += idle_time
        self.setup_total_time = self.setup_active_time + self.setup_idle_time
        self.machining_time = machining_time
        self.is_finished = True


# Machine state, all dynamic data of the machine's state
class Machine_state(models.Model):
    status = models.CharField(max_length=20, default=strings.machine_stopped)
    current_tool = models.CharField(max_length=10, default=1, null=True)
    current_M_code = models.CharField(max_length=10, default=0, null=True)
    mode = models.CharField(max_length=25, default=strings.mode_auto)
    active_nc_program = models.CharField(max_length=50, default='O00000')
    current_machine_time = models.DateTimeField(default=defaults.midnight_january_first)
    this_cycle_duration = models.DurationField(blank=True, default=defaults.duration_zero)
    remain_time = models.DurationField(blank=True, default=defaults.duration_zero)
    last_cycle_duration =  models.DurationField(default=defaults.duration_zero)
    m30_counter2 = models.IntegerField(default=0)
    m30_counter1 = models.IntegerField(default=0)
    change_status_file_number = models.IntegerField(default=0)
    is_current_state = models.BooleanField(default=True, blank=None, null=None)

    def __str__(self) -> str:
        return f"Current {self.active_nc_program}" if self.is_current_state else f"Previous {self.active_nc_program}"
    
    # get default state
    @classmethod
    def get_default_pk(cls):
        machine_state, created = cls.objects.get_or_create(
            )
        return machine_state.pk

    # Method to set state from POST request, from a query dict
    def set_state_from_POST(self, post_dict: dict) -> None:
        # Dictionary of expected keys and their corresponding parsing functions
        # Note: Some keys might need custom parsing or default values, adjust accordingly
        expected_keys = {
            'status': None,
            'current_tool': None,
            'current_M_code': None,
            'mode': None,
            'active_nc_program': None,
            'current_machine_time': parse_datetime,
            # in csv's the keys are written "this_cycle" and "last_cycle"
            # but in the state model they are written "this_cycle_duration" and "last_cycle_duration"
            'this_cycle': timedelta_from_string,
            'last_cycle': timedelta_from_string,
            'remain_time': timedelta_from_string,
            'm30_counter2': int,
            'm30_counter1': int
        }

        # Iterate over the expected keys and update only if they exist in post_dict
        for key, parse_func in expected_keys.items():
            if key in post_dict:
                # If a parsing function is specified, use it, otherwise assign directly
                if parse_func:
                    # Special case for this_cycle and last_cycle
                    if key == 'this_cycle':
                        setattr(self, 'this_cycle_duration', parse_func(post_dict[key]))
                    elif key == 'last_cycle':
                        setattr(self, 'last_cycle_duration', parse_func(post_dict[key]))
                    # General case
                    else:
                        setattr(self, key, parse_func(post_dict[key]))
                else:
                    setattr(self, key, post_dict[key])

        self.is_current_state = True 

    # Method to flag this state as previous state
    def make_previous(self):
        self.is_current_state = False
 

# Model of a machine.
class Machine(models.Model):
    name = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(default=defaults.default_IP)    
    active_job = models.ForeignKey(Job, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    active_cycle = models.ForeignKey('monitoring.Cycle', on_delete=models.SET_DEFAULT, related_name='active_cycle', default=None, blank=True, null=True)
    previous_cycle = models.ForeignKey('monitoring.Cycle', on_delete=models.SET_DEFAULT, related_name='previous_cycle', default=None, blank=True, null=True)
    status = models.CharField(max_length=20, default=strings.machine_stopped)
    current_tool = models.CharField(max_length=10, default=None, null=True)
    mode = models.CharField(max_length=25, default=strings.mode_auto)
    remain_time = models.DurationField(blank=True, default=defaults.duration_zero)
    this_cycle_duration = models.DurationField(blank=True, default=defaults.duration_zero)
    active_nc_program =models.CharField(max_length=50, default='')
    last_end_cycle_time =  models.DateTimeField(default=defaults.midnight_january_first)
    last_cycle_duration =  models.DurationField(default=defaults.duration_zero)
    current_machine_time = models.DateTimeField(default=defaults.midnight_january_first)
    last_active_time =  models.DateTimeField(default=defaults.midnight_january_first)
    inactive_time =  models.DurationField(default=defaults.duration_zero)
    # last time when the machine was active
    last_start = models.DateTimeField(default=defaults.midnight_january_first)
    # last time when machine was stoped
    last_stop = models.DateTimeField(default=defaults.midnight_january_first)
    next_offline_file = models.IntegerField(default=0)
    last_offline_file = models.IntegerField(default=0)
    last_offline_date = models.DateField(default=defaults.january_the_first)
    m30_counter2 = models.IntegerField(default=0)
    m30_counter1 = models.IntegerField(default=0)
    # current machine state
    current_state = models.ForeignKey(
        Machine_state, 
        verbose_name='current', 
        on_delete=models.SET_DEFAULT, 
        default=Machine_state.get_default_pk,
        related_name='current_machines',
        )
    # last machine state
    last_state = models.ForeignKey(
        Machine_state, 
        verbose_name='last', 
        on_delete=models.SET_DEFAULT, 
        default=Machine_state.get_default_pk,
        related_name='last_machines',
        )
    tools_maximum = models.IntegerField(default=40)
    mtconnect_port = models.IntegerField(default=8082, validators=[MaxValueValidator(9000), MinValueValidator(5000)])
    dprnt_port = models.IntegerField(default=2027, validators=[MaxValueValidator(9000), MinValueValidator(1000)])
    network_name = models.CharField(max_length=20, default=defaults.machine_network_name_unknown)

    class Meta:
        verbose_name = ("Machine")
        verbose_name_plural = ("Machines")

    def __str__(self):
        return self.name
    
    # get default machine 
    @classmethod
    def get_default_pk(cls):
        machine, created = cls.objects.get_or_create(
            name = 'Unknown',
            )
        return machine.pk

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("Machine_detail", kwargs={"pk": self.pk})

    # Method to read data from the machine thru DPRNT
    def read_dprint(self):
        sock = socket.socket
        with sock.connect(self.ip_address, self.dprnt_port) as dprnt:
            recieved = dprnt.rect(1024)
        return recieved
    
    # Method to switch machine statuses
    # current status becames previous
    def switch_statuses(self):
        buffer_state = self.last_state
        self.last_state = self.current_state
        self.last_state.is_current_state = False
        self.current_state = buffer_state
        self.current_state.is_current_state = True

    # Methon to log the status change
    def log_status_change(self) -> bool:
        last = self.last_state
        current = self.current_state

        # machine has not change status
        if last.status == current.status:
            # machine stands 'STOPPED' -> 'STOPPED'
            if last.status in strings.stopped_statuses and current.status in strings.stopped_statuses:
                self.inactive_time = self.inactive_time + (current.current_machine_time - last.current_machine_time)
            # machine is active 'ACTIVE' -> 'ACTIVE'
            if last.status == strings.machine_active and current.status == strings.machine_active:
                self.inactive_time = timedelta(0)
                self.last_start = current.current_machine_time
        # machine stands 'STOPPED' -> 'FEED_HOLD'
        elif last.status in strings.stopped_statuses and current.status in strings.stopped_statuses:
            self.inactive_time = self.inactive_time + (current.current_machine_time - last.current_machine_time)
        # machine has changed status
        else:
            # check activity
            day_activity_log = Day_activity_log.objects.filter(day=self.get_current_day(), machine=self)
            if len(day_activity_log) == 0:
                day_activity_log = Day_activity_log(day=self.get_current_day(), machine=self)
                day_activity_log.starts = self.current_machine_time
                self.last_start = self.current_machine_time
            else:
                day_activity_log = day_activity_log.get()
            # machine stoped 'ACTIVE' -> 'STOPPED'
            if self.is_changed_active_stop() or self.is_changed_active_feed_hold():
                # write info to day_activity_log
                day_activity_log.total_active += self.current_machine_time - self.last_start
                self.last_stop = self.current_machine_time
                self.last_start = last.current_machine_time
                self.inactive_time = current.current_machine_time - last.current_machine_time
            # machine is active 'STOPED' -> 'ACTIVE'
            if self.is_changed_stop_active() or self.is_changed_feed_hold_active():
                day_activity_log.total_stoped += self.current_machine_time - self.last_stop
                self.last_start = self.current_machine_time
            day_activity_log.ends = self.current_machine_time
            day_activity_log.save()


    # Method to check if status has changed from 'STOPPED' to 'ACTIVE'
    def is_changed_stop_active(self) -> bool:
        last = self.last_state
        current = self.current_state
        if last.status in strings.stopped_statuses and current.status == strings.machine_active:
            return True
        return False
    
    # Method to check if status has changed from 'ACTIVE' to 'STOPPED'
    def is_changed_active_stop(self) -> bool:
        last = self.last_state
        current = self.current_state
        if last.status == strings.machine_active and current.status in strings.stopped_statuses:
            return True
        return False
    
    # Method to check if status has changed from 'ACTIVE' to 'FEED_HOLD'
    def is_changed_active_feed_hold(self) -> bool:
        last = self.last_state
        current = self.current_state
        if last.status == strings.machine_active and current.status == strings.machine_feed_hold:
            return True
        return False
    
    # Method to check if status has changed from 'FEED_HOLD' to 'ACTIVE'
    def is_changed_feed_hold_active(self) -> bool:
        last = self.last_state
        current = self.current_state
        if last.status == strings.machine_feed_hold and current.status == strings.machine_active:
            return True
        return False

    # Method to check if nc program has changed
    def is_changed_nc_program(self) -> bool:
        if self.last_state.active_nc_program != self.current_state.active_nc_program:
            print(self.last_state.active_nc_program, ' and ',self.current_state.active_nc_program)
            return True
        return False
        
    # Method to check if machine started new Job
    def is_started_new_job(self):
        last = self.last_state
        current = self.current_state
        # Check if the name of .NC program has changed
        if current.active_nc_program != last.active_nc_program:
            return True
        
    # Method to check if the previous job was reselcted
    def is_previous_job(self):
        recent_jobs = Job.objects.all().order_by('-started')[:2] 
        # Check if the current NC program matches any of these recent jobs
        current_nc_program = self.active_nc_program
        for job in recent_jobs:
            if job.nc_program == current_nc_program:
                # If a match is found, it means a previous job with the same NC program was selected
                return True, job  # Return True and the matching job instance

        return False, None  # Return False if no match is found
    
    # Method to handle jobs started by selecting NC program
    def handle_middle_job(self):
        recent_jobs = Job.objects.all().order_by('-started')[:2]
        middle_job = None
        for job in recent_jobs:
            if job.nc_program != self.active_nc_program:
                middle_job = self.active_job
                break
        if middle_job and not middle_job.is_finished:
            middle_job.ended = self.current_machine_time
            middle_job.finished()
            middle_job.save()


    
    # Method to start new Job
    def start_new_job(self):
        # finish active if exists
        if self.active_job is not None:
            self.job_finished()

        # Check if the machine should continue a previous job
        has_previous_job, previous_job = self.is_previous_job()
        if has_previous_job:
            # If there's a previous job, resume it
            self.active_job = previous_job
            self.handle_middle_job()
            print(f"Resuming previous job: {previous_job.nc_program}")
        else:
            # start new job 
            job = Job()
            job.started = self.current_machine_time
            job.nc_program = self.active_nc_program
            self.active_job = job
            job.save()

        self.save()

    # Method to check if the job is finished
    def is_job_finished(self):
        return self.active_job.is_finished()

    # Method to do if the job is finished
    def job_finished(self):
        if self.active_job:
            self.active_job.ended = self.current_machine_time
            self.active_job.finished()
            self.active_job.save()
            self.active_job = None

    # Method to check if machine has changed cycle, started cycle or finished cycle
    def check_cycle(self) -> None:
        last = self.last_state
        current = self.current_state

        # check if nc program has changed
        if self.is_changed_nc_program():
            if self.active_cycle is not None:
                self.active_cycle.hard_finish()
                self.active_cycle = None
            self.job_finished()

 
        # check if machine has an active cycle
        if self.active_cycle is not None:
            # if the cycle was finished
            is_cycle_finished, was_finished_yesterday = self.is_finished_cycle()
            if is_cycle_finished:
                # if the cycle was finished yesterday
                if was_finished_yesterday:
                    self.finished_cycle(finished_yesterday=True)
                else:
                    self.finished_cycle()
            # if the cycle wasn't finished
            else:
                self.continue_current_cycle()
        # if machine has no current cycle
        else:
            # if machine started new cycle
            if self.is_started_new_cycle():
                self.start_new_cycle()
                

        # check if machine changed tool
        if self.is_tool_changed():
            self.tool_change()
     
    # Method to check if the cycle is finished
    def is_finished_cycle(self):
        last = self.last_state
        current = self.current_state
        # check if machine has finished the cycle
        if last.status in [strings.machine_active, strings.machine_feed_hold] and current.status == strings.machine_stopped:
            if last.current_machine_time.day != current.current_machine_time.day:
                return True, True
            return True, False
        if current.m30_counter1 > last.m30_counter1 or current.m30_counter2 > last.m30_counter2:
            # if the cycle was finished yesterday it's finished time and duration
            # has to be set by last state current_machine_time
            if last.current_machine_time.day != current.current_machine_time.day:
                return True, True
            return True, False
        else:
            return False, False

    # Method to do when the cycle was finished
    def finished_cycle(self, finished_yesterday=None):
        last = self.last_state
        current = self.current_state

        cycle = self.active_cycle
        # set cycle duration when cycle was finished yesterday
        if finished_yesterday:
            cycle.finish(finished_yesterday=True, finished_time=last.current_machine_time)
        # set cycle duration when cycle was finished today
        else:
            cycle.finish()
            # check if cycle is warm up cycle
            cycle.is_warm_up_cycle()
            # check if cycle is full cycle
            # check if cycle is setting cycle

        # do if machine finished a cycle of the active job
        if self.active_job is not None:
            # Add one to job only if the cycle is full cycle
            if self.active_job.full_cycle:
                is_full_cycle = self.active_job.compare_to_full_cycle(cycle)
                if is_full_cycle:
                    self.active_job.add_one_cycle()
                # check if last two partial cycles combined are equal to full cycle
                elif self.active_job.check_for_broken_cycle(cycle):
                    self.active_job.add_one_cycle()
            # Update current job
            self.active_job.cycle_time = self.active_job.get_cycle_time()
            self.active_job.part_changing_time = self.active_job.get_changing_time()
            self.active_job.get_ended()
            self.active_job.find_full_cycle()
            self.active_job.save()

            # check if job is finished
            if self.is_job_finished():
                self.job_finished()
        # case if cycle was finished without active job
        else:
            print(f"{self.name} has finished a cycle without active job")

        # save cycle and set active cycle to None
        cycle.save()
        self.active_cycle = None

    # Method to check if machine started new cycle
    def is_started_new_cycle(self):
        last = self.last_state
        current = self.current_state
        # new cycle started when machine change from 'STOPPED' to 'ACTIVE'
        if last.status ==  strings.machine_stopped and current.status == strings.machine_active:
            return True
        # new cycle started when machine has no active cycle, is in 'AUTO' mode
        # and has status 'ACTIVE'
        if not self.active_cycle and current.status == strings.machine_active and current.mode == strings.mode_auto:
            return True
        return False

    # Methond to do if machine started new cycle
    def start_new_cycle(self):
        last = self.last_state
        current = self.current_state
        # finich active cycle if exists
        if self.active_cycle is not None:
            self.finished_cycle()
        # create new cycle
        cycle = Cycle()
        cycle.mode = current.mode
        print(f'Started new cycle | MODE : {current.mode}')
        # start new job if machine has no active job
        if self.active_job is None:
            # to do:
            # check for previous job, case where nc program was selected
            # but no cycles was run
            # =========================================================
            # start new job only if machine is in 'AUTO' mode
            if current.mode == strings.mode_auto:
                self.start_new_job()
        # write cycle parameters from current state
        cycle.start(machine=self)
        # update machine, set this cycle as active_cycle
        self.active_cycle = cycle

    # Method if state was finished but the cycle continues
    def continue_current_cycle(self):
        last = self.last_state
        current = self.current_state
        pass

    # Method to continue the Job
    def continue_job(self):
        pass
    
    # Method to check if machine has changed a tool
    def is_tool_changed(self) -> bool:
        last = self.last_state
        current = self.current_state
        if current.current_tool != last.current_tool:
            return True
        return False
    
    # Method to do when machine changed tool
    def tool_change(self) -> None:
        current = self.current_state
        if self.active_cycle:
            self.active_cycle.add_tool(current.current_tool)

    # Method to update the machine from current Machine_state
    def update_from_state(self) -> None:

        current = self.current_state

        self.status = current.status
        self.remain_time = current.remain_time
        self.last_cycle_duration = current.last_cycle_duration
        self.this_cycle_duration = current.this_cycle_duration
        self.current_machine_time = current.current_machine_time
        self.m30_counter2 = current.m30_counter2
        self.m30_counter1 = current.m30_counter1
        self.active_nc_program = current.active_nc_program
        self.mode = current.mode
        self.current_tool = current.current_tool


    # Methon to check if the tool was changed
    def has_chanted_tool(self) -> bool:
        if self.current_tool != self.last_response['current_tool']:
            return True
        return False
    
    # Method to get current day from machine current time
    def get_current_day(self) -> date:
        current_time = self.current_machine_time
        day = date(year=current_time.year, month=current_time.month, day=current_time.day)
        return day

       
# Machine offline xml state
class Machine_Ofline_XML(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.SET_DEFAULT, default=Machine.get_default_pk)
    offline_file_number =  models.IntegerField(default=0)

    def __str__(self) -> str:
        result = f'{self.machine.name} : {self.offline_file_number}'
        return result

    def getXMl(self) -> str:
        subfolder = str(self.offline_file_number//500*500) + '-' + str(500*(self.offline_file_number//500+1)-1)
        today = testing_variables_defaut.today_offline_string
        file_name = f'{str(self.offline_file_number)}_{self.machine.name}.xml'
        document_path = path.join(testing_variables_defaut.offline_path_device, today, self.machine.name, subfolder, file_name)
        # check if offline file exists
        if not path.exists(document_path):
            result = ""
        else:
            with open (document_path, 'r') as xml_file:
                result = xml_file.read()         
        return result
    
    def add_one_offline(self) -> None:
        self.offline_file_number += 1

    def nextXMl(self) -> str:
        result = self.getXMl()
        self.add_one_offline()
        self.save()
        return result


# Log of activity of one day
class Day_activity_log(models.Model):
    machine = models.ForeignKey('Machine', on_delete=models.CASCADE, default=Machine.get_default_pk)
    day = models.DateField(default=datetime.now)
    starts =  models.DateTimeField(default=timezone.now)
    ends =  models.DateTimeField(default=timezone.now)
    total_active = models.DurationField(default=defaults.duration_zero)
    total_stoped = models.DurationField(default=defaults.duration_zero)


# Model of a cycle
class Cycle(models.Model):
    # change this to on_delete default and write default machine
    machine = models.ForeignKey(Machine, on_delete=models.SET_DEFAULT, default=Machine.get_default_pk)
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_DEFAULT,
        default=None,
        blank=True,
        null=True,
        db_index=True
        ) 
    duration = models.DurationField(default=defaults.duration_zero)
    tool_sequence = models.TextField(default=strings.empty_string)
    changing_time = models.DurationField(default=defaults.duration_zero)
    started = models.DateTimeField(auto_now=False, auto_now_add=False, db_index=True, default=defaults.midnight_january_first)
    mode = models.CharField(max_length=25, default=strings.mode_auto, db_index=True)
    is_still_running = models.BooleanField(default=True)
    is_setting_cycle = models.BooleanField(default=True)
    is_full_cycle = models.BooleanField(default=False)
    # this is warm up boolean attribute, cant name it is_warm_up_cycle because of django migrations
    is_warm_up = models.BooleanField(default=False)
    ended = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, db_index=True, default=None)
    finished_by = models.CharField(max_length=50, default=strings.empty_string)

    class Meta:
        ordering = ['-started']
        indexes = [
            models.Index(fields=['started', 'ended', 'job', 'mode']),
        ]
    
    def __str__(self):
        total_seconds = int(self.duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_mode = strings.MODE_FORMATTED_MAPPING.get(self.mode, strings.unknown_mode)

        if hours > 0:
            duration_format = f"{hours}:{minutes:02}:{seconds:02}"
        elif minutes > 0:
            duration_format = f"{minutes}:{seconds:02}"
        else:
            duration_format = f"{seconds} seconds"

        started_format = self.started.strftime('%d %b | %H:%M:%S')
        ended_format = self.ended.strftime('%H:%M:%S') if self.ended else 'Not finished'
        start_end_string = f'{started_format} - {ended_format}'
        if self.is_warm_up:
            return_string = f'Warm up: {duration_format} | {self.started.strftime("%d %b")}'
        else:
            return_string = f'{formatted_mode}:  {duration_format} | {start_end_string} | {self.machine.name} | {str(self.job)}'
        return return_string
    
    def start(self, machine:Machine):
        self.started = machine.current_machine_time
        self.machine = machine
        changing_time = machine.current_machine_time - machine.last_stop
        self.changing_time = round_to_seconds(changing_time)
        if self.changing_time < defaults.duration_zero:
            self.changing_time = defaults.duration_one_minute
        if self.changing_time > defaults.duration_one_hour:
            self.changing_time = defaults.duration_one_hour
        if self.machine.active_job and self.mode == strings.mode_auto:
            self.job = self.machine.active_job
        self.save()

    # Method to finish the cycle
    def finish(self, finished_yesterday=None, finished_time=None):
        if finished_yesterday:
            self.ended = finished_time
        else:
            self.ended = self.machine.current_machine_time
        duration = round_to_seconds(self.ended - self.started)
        self.duration = duration
        # check if the cycle is too long
        # only for testing
        if self.duration > defaults.duration_one_hour:
            self.duration = defaults.duration_one_hour
        self.check_tool_sequence()
        self.is_still_running = False
        self.finished_by = self.ended_by()
        self.save()

    # Method for hard finish of the cycle
    def hard_finish(self):
        # use this method if the job was finished by changing the nc program
        # or if the mode was changed to manual or mdi
        # or if the machine was turned off (not written yet)
        machine = self.machine
        current = machine.current_state
        last = machine.last_state
        self.check_tool_sequence()
        if current.current_machine_time.day != last.current_machine_time.day:
            self.ended = last.current_machine_time
            self.finish(finished_yesterday=True, finished_time=last.current_machine_time)
        else:
            self.finish()

    # Check for tool sequence, assign current tool if empty
    def check_tool_sequence(self):
        machine = self.machine
        if self.tool_sequence == strings.empty_string:
            self.tool_sequence = machine.current_tool
        
    # Method to write what was the cycle finished by
    def ended_by(self) -> str:
        return_string = f'Finished by unknown reason'
        parameters = ['status', 'mode', 'm30_counter2', 'm30_counter1', 'active_nc_program']
        for parameter in parameters:
            if getattr(self.machine.current_state, parameter) != getattr(self.machine.last_state, parameter):
                return_string = f'Finished  by {parameter}: {getattr(self.machine.last_state, parameter)} -> {getattr(self.machine.current_state, parameter)}'
                return return_string
        return return_string

    # Method to add tool to tool_sequence
    def add_tool(self, tool:str) -> None:
        if self.tool_sequence == '':
            self.tool_sequence = tool
        else:
            tool_sequence = self.tool_sequence.split(',')
            # add tools to the cycle only if the machine is in 'AUTO' mode
            if self.machine.current_state.mode == strings.mode_auto:
                # check if the tool was realy changed
                if tool_sequence[-1] != tool:
                    tool_sequence.append(tool)
                    self.tool_sequence = ','.join(tool_sequence)
        self.save()

    # Method to check if the cycle is warm up cycle
    def is_warm_up_cycle(self) -> bool:
        # check if the cycle is long enough
        if self.duration > defaults.warm_up_cycle_duration:
            # check if the cycle has only one tool change
            if len(self.tool_sequence.split(',')) <= 2:
                # check if the cycle was run in 'MANUAL_DATA_INPUT' mode
                if self.machine.current_state.mode == strings.mode_mdi:
                    self.is_warm_up = True
                    self.is_full_cycle = False
                    self.is_setting_cycle = False
                    self.save()
                    return True
                    
class Archived_cycle(models.Model):
    id = models.AutoField(primary_key=True)
    machine = models.ForeignKey(Machine, on_delete=models.SET_DEFAULT, default=Machine.get_default_pk)
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_DEFAULT,
        default=None,
        blank=True,
        null=True,
        db_index=True
        ) 
    duration = models.DurationField(default=defaults.duration_zero)
    tool_sequence = models.TextField(default=strings.empty_string)
    changing_time = models.DurationField(default=defaults.duration_zero)
    started = models.DateTimeField(auto_now=False, auto_now_add=False, db_index=True, default=defaults.midnight_january_first)
    ended = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, db_index=True, default=None)
    finished_by = models.CharField(max_length=50, default=strings.empty_string)


    class Meta:
        verbose_name = 'Archived Cycle'
        verbose_name_plural = 'Archived Cycles'

    def copy_from_cycle(self, cycle:Cycle) -> None:
        self.machine = cycle.machine
        self.job = cycle.job
        self.duration = cycle.duration
        self.tool_sequence = cycle.tool_sequence
        self.changing_time = cycle.changing_time
        self.started = cycle.started
        self.ended = cycle.ended
        self.finished_by = cycle.finished_by

# Create your models here.

from django.urls import path
from . import views

urlpatterns = [
    # --------------------
    # 📊 Main Dashboard Views
    # --------------------
    path('', views.home, name='dashboard-home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proxy/', views.proxy, name='dashboard-proxy'),
    path('about/', views.about, name='dashboard-about'),

    # --------------------
    # 🛠️ Machine and Job Detail Views
    # --------------------
    path('machine/<int:machine_id>/', views.machine_detail, name='machine_detail'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/finish/<int:job_id>/', views.finish_job, name='finish_job'),
    path('job/unarchive/<int:job_id>/', views.unarchive_job, name='unarchive_job'),

    # --------------------
    # 📈 Job Analysis & Timeline
    # --------------------
    path('get-job-productivity/<int:pk>/', views.get_job_productivity, name='get_job_productivity'),
    path('cycle_timeline/<int:job_id>/', views.cycle_timeline, name='cycle_timeline'),

    # --------------------
    # 📋 Next Jobs Display + Auto-Update
    # --------------------
    path('next-jobs/', views.next_jobs_view, name='next_jobs'),
    path('check-next-jobs/', views.check_next_jobs, name='check_next_jobs'),
    path("current-jobs/", views.current_jobs_view, name="current_jobs"),
    # path("check-current-jobs/", views.check_current_jobs, name="check_current_jobs"),

    # --------------------
    # 🔄 Update APIs (called from machine scripts or automation)
    # --------------------
    path('api/login/', views.api_login_view, name='api_login'),
    path("api/logout/", views.api_logout_view, name="api_logout"),

    # --------------------
    # 📱 Mobile API Endpoints
    # --------------------
    path('api/mobile/dashboard/', views.mobile_dashboard, name='mobile_dashboard'),

    # --------------------
    # 🔧 Machine Operation Assignment API
    # --------------------
    path('api/sync-operation-pool/', views.sync_operation_pool, name='sync_operation_pool'),
    path('api/monitor-assign-operation/', views.monitor_assign_operation, name='monitor_assign_operation'),
    path('api/manual-assign-operation/', views.manual_assign_operation, name='manual_assign_operation'),
    path('api/toggle-operation-status/', views.toggle_operation_status, name='toggle_operation_status'),
    path('api/available-operations/', views.get_available_operations, name='get_available_operations'),
    path('api/machine-assignments/<int:machine_id>/', views.get_machine_assignments, name='get_machine_assignments'),

    # --------------------
    # 🖼️ Drawing Monitor API
    # --------------------
    path('api/drawing/set-cursor/', views.set_drawing_cursor, name='set_drawing_cursor'),
    path('api/drawing/cursor-status/', views.get_cursor_status, name='get_cursor_status'),
    path('api/drawing/all/', views.get_all_drawings, name='get_all_drawings'),

    # --------------------
    # 📋 Planning Interface (Admin)
    # --------------------
    path('planning/', views.planning_grid, name='planning_grid'),
    path('planning/<int:machine_id>/', views.planning_detail, name='planning_detail'),

    # --------------------
    # 🖼️ Drawing Monitor Display
    # --------------------
    path('drawing-monitor/', views.drawing_monitor, name='drawing_monitor'),
    path('cursor-test/', views.cursor_test, name='cursor_test'),

    path("save_subscription/", views.save_subscription, name="save_subscription"),
    path("unsubscribe/", views.unsubscribe, name="unsubscribe"),
    path("subscribe_machine/", views.subscribe_machine, name="subscribe_machine"),
    path("unsubscribe_machine/", views.unsubscribe_machine, name="unsubscribe_machine"),
    path("my_subscriptions/", views.my_subscriptions, name="my_subscriptions"),
    path("api/subscriptions/<int:machine_id>/", views.get_machine_subscriptions, name="get_machine_subscriptions"),
    path('update-next-monitor-operation/', views.update_next_monitor_operation, name='update_next_monitor_operation'),
    path('update-current-monitor-operation/', views.update_current_monitor_operation, name='update_current_monitor_operation'),
    path('update-machine-status/', views.update_machine_status, name='update_machine_status'),
    

    # --------------------
    # 🔔 Notification
    # --------------------
    path("trigger_notification", views.trigger_notification, name="api_trigger_notification"),
    path("machine-subscribe/<int:machine_id>/", views.machine_subscribe_view, name="machine_subscribe"),
    path("manifest/<int:machine_id>.json", views.dynamic_manifest, name="dynamic_manifest"),
    path("service-worker.js", views.service_worker, name="service_worker"),
    path("push-test/", views.push_test_view, name="push_test"),
    path("send_to_subscription/", views.send_to_subscription, name="send_to_subscription"),
    


    # --------------------
    # 🔐 Web Push Configuration (for frontend JS)
    # --------------------
    path('webpush/public_key/', views.get_webpush_public_key, name='webpush_public_key'),
    path("save_subscription/", views.save_subscription, name="save_subscription"),
]

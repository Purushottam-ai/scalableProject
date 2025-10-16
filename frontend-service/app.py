import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from config import config

# Configure Streamlit page
st.set_page_config(
    page_title="Personal Task & Reminder App",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TaskManager:
    def __init__(self):
        self.task_service_url = config.TASK_SERVICE_URL
        self.notification_service_url = config.NOTIFICATION_SERVICE_URL
    
    def get_tasks(self, status=None, priority=None, search=None) -> List[Dict]:
        """Get tasks from the task service"""
        try:
            params = {}
            if status:
                params['status'] = status
            if priority:
                params['priority'] = priority
            if search:
                params['search'] = search
                
            response = requests.get(f"{self.task_service_url}/tasks", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to fetch tasks: {e}")
            return []
    
    def create_task(self, task_data: Dict) -> Optional[Dict]:
        """Create a new task"""
        try:
            response = requests.post(f"{self.task_service_url}/tasks", json=task_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to create task: {e}")
            return None
    
    def update_task(self, task_id: str, task_data: Dict) -> Optional[Dict]:
        """Update an existing task"""
        try:
            response = requests.put(f"{self.task_service_url}/tasks/{task_id}", json=task_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to update task: {e}")
            return None
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            response = requests.delete(f"{self.task_service_url}/tasks/{task_id}")
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to delete task: {e}")
            return False
    
    def complete_task(self, task_id: str) -> Optional[Dict]:
        """Mark a task as completed"""
        try:
            response = requests.patch(f"{self.task_service_url}/tasks/{task_id}/complete")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to complete task: {e}")
            return None
    
    def get_task_stats(self) -> Optional[Dict]:
        """Get task statistics"""
        try:
            response = requests.get(f"{self.task_service_url}/tasks/stats/overview")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to fetch task statistics: {e}")
            return None
    
    def get_notifications(self) -> List[Dict]:
        """Get notification history"""
        try:
            response = requests.get(f"{self.notification_service_url}/notifications/history")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to fetch notifications: {e}")
            return []
    
    def get_reminders(self) -> List[Dict]:
        """Get reminders"""
        try:
            response = requests.get(f"{self.notification_service_url}/reminders")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to fetch reminders: {e}")
            return []

def main():
    st.title("📋 Personal Task & Reminder App")
    st.markdown("---")
    
    task_manager = TaskManager()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Tasks", "Create Task", "Notifications", "Analytics"]
    )
    
    if page == "Dashboard":
        show_dashboard(task_manager)
    elif page == "Tasks":
        show_tasks(task_manager)
    elif page == "Create Task":
        show_create_task(task_manager)
    elif page == "Notifications":
        show_notifications(task_manager)
    elif page == "Analytics":
        show_analytics(task_manager)

def show_dashboard(task_manager: TaskManager):
    """Display the main dashboard"""
    st.header("📊 Dashboard")
    
    # Get task statistics
    stats = task_manager.get_task_stats()
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tasks", stats.get('total_tasks', 0))
        with col2:
            st.metric("Pending", stats.get('pending_tasks', 0))
        with col3:
            st.metric("Completed", stats.get('completed_tasks', 0))
        with col4:
            st.metric("Overdue", stats.get('overdue_tasks', 0), delta=f"-{stats.get('overdue_tasks', 0)}")
    
    # Recent tasks
    st.subheader("📝 Recent Tasks")
    recent_tasks = task_manager.get_tasks()[:5]  # Get first 5 tasks
    
    if recent_tasks:
        for task in recent_tasks:
            # Handle different possible ID field names
            task_id = task.get('id') or task.get('_id') or task.get('task_id')
            
            with st.expander(f"{task.get('title', 'Untitled')} ({task.get('status', 'unknown')})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Description:** {task.get('description', 'No description')}")
                    st.write(f"**Priority:** {task.get('priority', 'medium')}")
                    st.write(f"**Category:** {task.get('category', 'General')}")
                    if task.get('due_date'):
                        st.write(f"**Due Date:** {task['due_date']}")
                
                with col2:
                    if task.get('status') != 'completed' and task_id:
                        if st.button(f"Complete", key=f"complete_{task_id}"):
                            result = task_manager.complete_task(str(task_id))
                            if result:
                                st.success("Task completed!")
                                st.experimental_rerun()
                    
                    if task_id:
                        if st.button(f"Delete", key=f"delete_{task_id}"):
                            if task_manager.delete_task(str(task_id)):
                                st.success("Task deleted!")
                                st.experimental_rerun()
    else:
        st.info("No tasks found. Create your first task!")

def show_tasks(task_manager: TaskManager):
    """Display and manage tasks"""
    st.header("📋 Task Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "pending", "in_progress", "completed", "cancelled"]
        )
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "low", "medium", "high", "urgent"]
        )
    with col3:
        search_term = st.text_input("Search Tasks")
    
    # Apply filters
    status = None if status_filter == "All" else status_filter
    priority = None if priority_filter == "All" else priority_filter
    search = search_term if search_term else None
    
    tasks = task_manager.get_tasks(status=status, priority=priority, search=search)
    
    if tasks:
        for i, task in enumerate(tasks):
            # Handle different possible ID field names
            task_id = task.get('id') or task.get('_id') or task.get('task_id')
            
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{task.get('title', 'Untitled')}**")
                    st.write(f"Status: {task.get('status', 'unknown')} | Priority: {task.get('priority', 'medium')}")
                    if task.get('description'):
                        st.write(f"_{task['description'][:100]}{'...' if len(task.get('description', '')) > 100 else ''}_")
                
                with col2:
                    if task.get('status') != 'completed' and task_id:
                        if st.button("✅", key=f"complete_btn_{task_id}", help="Complete Task"):
                            result = task_manager.complete_task(str(task_id))
                            if result:
                                st.success("Task completed!")
                                st.experimental_rerun()
                
                with col3:
                    if task_id:
                        if st.button("✏️", key=f"edit_btn_{task_id}", help="Edit Task"):
                            st.session_state[f"edit_task_{task_id}"] = True
                
                with col4:
                    if task_id:
                        if st.button("🗑️", key=f"delete_btn_{task_id}", help="Delete Task"):
                            if task_manager.delete_task(str(task_id)):
                                st.success("Task deleted!")
                                st.experimental_rerun()
                
                st.markdown("---")
    else:
        st.info("No tasks found matching your criteria.")

def show_create_task(task_manager: TaskManager):
    """Create a new task"""
    st.header("➕ Create New Task")
    
    # Check if task was just created and show celebration
    if st.session_state.get('task_created', False):
        st.success("🎉 Task created successfully! 🎉")
        # Clear the flag
        del st.session_state.task_created
    
    with st.form("create_task_form"):
        title = st.text_input("Task Title *", max_chars=200)
        description = st.text_area("Description", max_chars=1000)
        
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"])
            category = st.text_input("Category", max_chars=100)
        
        with col2:
            due_date = st.date_input("Due Date (Optional)")
            due_time = st.time_input("Due Time (Optional)")
        
        reminder_enabled = st.checkbox("Enable Reminder")
        reminder_datetime = None
        
        if reminder_enabled:
            col3, col4 = st.columns(2)
            with col3:
                reminder_date = st.date_input("Reminder Date")
            with col4:
                reminder_time = st.time_input("Reminder Time")
            
            if reminder_date and reminder_time:
                reminder_datetime = datetime.combine(reminder_date, reminder_time).isoformat()
        
        submitted = st.form_submit_button("Create Task")
        
        if submitted:
            if not title.strip():
                st.error("Task title is required!")
            else:
                # Prepare task data
                task_data = {
                    "title": title.strip(),
                    "description": description.strip(),
                    "priority": priority,
                    "category": category.strip() if category.strip() else "General",
                    "status": "pending"
                }
                
                # Add due date if provided
                if due_date:
                    due_datetime = datetime.combine(due_date, due_time).isoformat()
                    task_data["due_date"] = due_datetime
                
                # Add reminder if enabled
                if reminder_enabled and reminder_datetime:
                    task_data["reminder_datetime"] = reminder_datetime
                
                # Create the task
                result = task_manager.create_task(task_data)
                if result:
                    st.success("Task created successfully!")
                    st.balloons()
                    # Use session state to trigger rerun after balloon effect
                    st.session_state.task_created = True

def show_notifications(task_manager: TaskManager):
    """Display notifications and reminders"""
    st.header("🔔 Notifications & Reminders")
    
    tab1, tab2 = st.tabs(["📬 Notifications", "⏰ Reminders"])
    
    with tab1:
        st.subheader("Notification History")
        notifications = task_manager.get_notifications()
        
        if notifications:
            for notification in notifications:
                with st.expander(f"{notification.get('title', 'Notification')} - {notification.get('created_at', '')}"):
                    st.write(f"**Message:** {notification.get('message', 'No message')}")
                    st.write(f"**Type:** {notification.get('type', 'unknown')}")
                    st.write(f"**Status:** {notification.get('status', 'unknown')}")
        else:
            st.info("No notifications found.")
    
    with tab2:
        st.subheader("Scheduled Reminders")
        reminders = task_manager.get_reminders()
        
        if reminders:
            for reminder in reminders:
                with st.expander(f"Reminder for: {reminder.get('task_title', 'Task')}"):
                    st.write(f"**Scheduled for:** {reminder.get('scheduled_time', 'Not set')}")
                    st.write(f"**Message:** {reminder.get('message', 'No message')}")
                    st.write(f"**Status:** {reminder.get('status', 'unknown')}")
        else:
            st.info("No reminders found.")

def show_analytics(task_manager: TaskManager):
    """Display analytics and charts"""
    st.header("📈 Analytics")
    
    # Get task statistics
    stats = task_manager.get_task_stats()
    tasks = task_manager.get_tasks()
    
    if stats and tasks:
        col1, col2 = st.columns(2)
        
        with col1:
            # Task status distribution
            status_data = {
                'Status': ['Pending', 'In Progress', 'Completed', 'Cancelled'],
                'Count': [stats['pending_tasks'], stats['in_progress_tasks'], 
                         stats['completed_tasks'], stats['cancelled_tasks']]
            }
            
            fig_status = px.pie(
                values=status_data['Count'],
                names=status_data['Status'],
                title="Task Status Distribution"
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Priority distribution
            df = pd.DataFrame(tasks)
            if not df.empty:
                priority_counts = df['priority'].value_counts()
                
                fig_priority = px.bar(
                    x=priority_counts.index,
                    y=priority_counts.values,
                    title="Tasks by Priority",
                    labels={'x': 'Priority', 'y': 'Number of Tasks'}
                )
                st.plotly_chart(fig_priority, use_container_width=True)
        
        # Task creation timeline
        if tasks:
            df = pd.DataFrame(tasks)
            df['created_date'] = pd.to_datetime(df['created_at']).dt.date
            daily_tasks = df.groupby('created_date').size().reset_index(name='count')
            
            fig_timeline = px.line(
                daily_tasks,
                x='created_date',
                y='count',
                title="Task Creation Timeline",
                labels={'created_date': 'Date', 'count': 'Tasks Created'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Key metrics
        st.subheader("📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            completion_rate = (stats['completed_tasks'] / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        with col2:
            st.metric("Overdue Tasks", stats['overdue_tasks'])
        
        with col3:
            st.metric("Upcoming Tasks", stats['upcoming_tasks'])
        
        with col4:
            pending_rate = (stats['pending_tasks'] / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
            st.metric("Pending Rate", f"{pending_rate:.1f}%")
    
    else:
        st.info("Create some tasks to see analytics!")

if __name__ == "__main__":
    main()
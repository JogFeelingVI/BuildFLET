# -*- coding: utf-8 -*-
# @Author: Your name
# @Date:   2025-03-04 20:30:55
# @Last Modified by:   Your name
# @Last Modified time: 2025-03-15 09:03:30
import flet as ft, json, random, string

def generate_unique_id(length=8):
    characters = string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for _ in range(length))
    return unique_id

class taskExc(ft.Column):
    def __init__(self, Name, Task_status, Task_delete, Task_edit, unique_id=None):
        super().__init__()
        self.Name = Name
        self.unique_id = generate_unique_id() if unique_id is None else unique_id
        self.Task_delete = Task_delete
        self.Task_status = Task_status
        self.Task_edit = Task_edit
        self.display_checkbox = ft.Checkbox(value=False, label=self.Name, on_change=self.status_change)
        self.completed = self.display_checkbox.value
        self.edit_name = ft.TextField(expand=1)
        
        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_checkbox,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(ft.Icons.EDIT, on_click=self.edit_clicked, tooltip="Edit"),
                        ft.IconButton(ft.Icons.DELETE, on_click=self.delete_clicked, tooltip="Delete"),
                    ]
                )
            ]
        )
        
        self.edit_view = ft.Row(
            visible=False,
            controls=[
                self.edit_name,
                ft.IconButton(ft.Icons.SAVE, on_click=self.save_clicked),
                ],
        )
        self.controls = [self.display_view, self.edit_view]
        
    def status_change(self, e):
        self.completed = self.display_checkbox.value
        self.Task_status()

    def edit_clicked(self, e):
        self.edit_name.value = self.Name
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()
        
    def save_clicked(self, e):
        self.display_checkbox.label = self.edit_name.value
        self.Name = self.display_checkbox.label
        self.edit_view.visible = False
        self.display_view.visible = True
        self.Task_edit()
        self.update()
        
    def delete_clicked(self, e):
        self.Task_delete(self)
        
    
        

class TodoApp(ft.Column):
    def __init__(self):
        super().__init__()
        self.data_file = "./data.json"
        self.Dataed = {}
        self.new_task = ft.TextField(hint_text="What needs to be done?", expand=True, on_submit=self.submit)
        self.tasks = ft.Column()
        self.items_count = ft.Text(value="0 items", color=ft.Colors.WHITE, size=16)
        self.filter = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="All"),
                ft.Tab(text="Active"),
                ft.Tab(text="Completed"),
            ],
            on_change=self.filter_change,
        )
        self.controls = [
            ft.Row(
                [self.new_task,
                ft.FloatingActionButton(text="ADD", icon=ft.Icons.ADD, on_click=self.add_click, tooltip='Add Task')],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            self.filter,
            self.tasks,
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.items_count,
                          ft.OutlinedButton(text="Clear Completed", icon=ft.Icons.DELETE, on_click=self.clear_clicked, tooltip='Clear Completed Tasks')
                          ],
            )
        ]
        self.load_data()
        
        
    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.delete_click(task)
                
    def submit(self, e):
        self.add_click(e)
    
    def add_click(self, e):
        if self.new_task.value == "":
            return
        self.tasks.controls.append(taskExc(Name=self.new_task.value, Task_status=self.task_status,Task_edit=self.task_edit, Task_delete=self.delete_click))
        self.new_task.value = ""
        self.update()
    
    def delete_click(self, e):
        self.Dataed.pop(f"{e.unique_id}")
        self.tasks.controls.remove(e)
        self.update()
        
    def filter_change(self, e):
        self.update()
        
    def task_status(self):
        self.update()
        
    def task_edit(self):
        self.update()
        
    def before_update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "All"
                or status == "Active" and task.completed == False
                or status == "Completed" and task.completed)
            if not task.completed:
                count += 1
            
            self.Dataed.update({f"{task.unique_id}": {"Name": task.Name, "completed": task.completed}})
        self.items_count.value = f"{count} active item(s) left"
        # print(f'[before_update save]')
        with open(self.data_file, "w") as f:
            json.dump(self.Dataed, f)
            
    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.Dataed = json.load(f)
        except FileNotFoundError:
            self.Dataed = {}
        
        if self.Dataed == {}:
            return
        tasks = []
        for id, task in self.Dataed.items():
            temp = taskExc(Name=task["Name"], Task_status=self.task_status, Task_edit=self.task_edit, Task_delete=self.delete_click, unique_id=id)
            if task["completed"]:
                temp.display_checkbox.value = True
                temp.completed = True
            tasks.append(temp)
        self.tasks.controls = tasks
        print(f'[load_data] {self.Dataed}')

def main(page: ft.Page):
    page.title = "To-Do List"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    todo = TodoApp()
    page.add(todo)

ft.app(main)

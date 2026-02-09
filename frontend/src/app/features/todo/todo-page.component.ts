import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TodoService } from '../../services/todo';

@Component({
  selector: 'app-todo-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './todo-page.component.html',
  styleUrls: ['./todo-page.component.css'],
})
export class TodoPageComponent implements OnInit {
  tasks: any[] = [];
  newTaskTitle: string = '';

  constructor(private todoService: TodoService) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.todoService.getTasks().subscribe((data) => (this.tasks = data));
  }

  ajouterTask(): void {
    if (this.newTaskTitle.trim()) {
      this.todoService.addTask(this.newTaskTitle).subscribe(() => {
        this.newTaskTitle = '';
        this.refresh();
      });
    }
  }

  supprimer(id: string): void {
    this.todoService.deleteTask(id).subscribe(() => this.refresh());
  }

  changerStatut(task: any): void {
    const nouveauStatut = !task.completed;
    this.todoService
      .toggleTask(task.id, nouveauStatut)
      .subscribe(() => this.refresh());
  }
}


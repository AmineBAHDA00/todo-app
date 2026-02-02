import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // Pour récupérer la saisie du clavier
import { TodoService } from './services/todo';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html', // On va modifier le HTML juste après
  styleUrls: ['./app.css']
})
export class AppComponent implements OnInit {
  tasks: any[] = [];
  newTaskTitle: string = '';
  

  constructor(private todoService: TodoService) {}

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    this.todoService.getTasks().subscribe(data => this.tasks = data);
  }

  ajouterTask() {
    if (this.newTaskTitle.trim()) {
      this.todoService.addTask(this.newTaskTitle).subscribe(() => {
        this.newTaskTitle = ''; // Vide le champ
        this.refresh(); // Recharge la liste
      });
    }
  }
  supprimer(id: string) {
  this.todoService.deleteTask(id).subscribe(() => this.refresh());
  }

  changerStatut(task: any) {
     const nouveauStatut = !task.completed;
     this.todoService.toggleTask(task.id, nouveauStatut).subscribe(() => this.refresh());
  }
}
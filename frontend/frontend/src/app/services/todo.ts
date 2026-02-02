import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class TodoService {
  private apiUrl = 'http://127.0.0.1:5000/tasks';

  constructor(private http: HttpClient) { }

  // Lire les tâches depuis Flask
  getTasks(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  // Envoyer une nouvelle tâche à Flask
  addTask(title: string): Observable<any> {
    return this.http.post<any>(this.apiUrl, { title });
  }
  // Supprimer
  deleteTask(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }

  // Modifier le statut
  toggleTask(id: string, isCompleted: boolean): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, { completed: isCompleted });
  }
}
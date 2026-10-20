import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterOutlet } from '@angular/router';
import { Navbar } from './layout/navbar/navbar';
import { Auth } from './core/auth/auth';
import { SystemHealth } from './core/models/auth.models';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterOutlet, Navbar],
  templateUrl: './app.html',
})
export class App {
  readonly authService = inject(Auth);

  activeTab = signal<'login' | 'register'>('login');
  email = '';
  password = '';
  fullName = '';
  errorMessage = signal<string | null>(null);
  isLoading = signal(false);
  health = signal<SystemHealth | null>(null);

  ngOnInit(): void {
    this.authService.checkHealth().subscribe({
      next: (res) => this.health.set(res),
      error: () => this.health.set(null),
    });
  }

  onSubmit(): void {
    this.errorMessage.set(null);
    this.isLoading.set(true);

    if (this.activeTab() === 'login') {
      this.authService.login({ email: this.email, password: this.password }).subscribe({
        next: () => {
          this.isLoading.set(false);
          this.email = '';
          this.password = '';
        },
        error: (err) => {
          this.isLoading.set(false);
          this.errorMessage.set(err.error?.detail || 'Login failed.');
        },
      });
    } else {
      this.authService
        .register({
          email: this.email,
          password: this.password,
          full_name: this.fullName || undefined,
        })
        .subscribe({
          next: () => {
            this.authService.login({ email: this.email, password: this.password }).subscribe({
              next: () => {
                this.isLoading.set(false);
                this.email = '';
                this.password = '';
                this.fullName = '';
              },
              error: (err) => {
                this.isLoading.set(false);
                this.errorMessage.set(err.error?.detail || 'Auto-login failed.');
              },
            });
          },
          error: (err) => {
            this.isLoading.set(false);
            this.errorMessage.set(err.error?.detail || 'Registration failed.');
          },
        });
    }
  }
}

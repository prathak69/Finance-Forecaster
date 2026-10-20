import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Auth } from '../../core/auth/auth';
@Component({
  selector: 'app-auth-component',
  imports: [CommonModule, FormsModule, RouterLink, ReactiveFormsModule],
  templateUrl: './auth-component.html',
  styleUrl: './auth-component.css',
})
export class AuthComponent {
  private readonly authService = inject(Auth);
  private readonly fb = inject(FormBuilder);

  readonly activeTab = signal<'login' | 'register'>('login');
  readonly errorMessage = signal<string | null>(null);
  readonly isLoading = signal(false);

  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(128)]],
  });

  registrationForm = this.fb.group({
    full_name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(128)]],
  });

  setTab(tab: 'login' | 'register') {
    this.activeTab.set(tab);
    this.errorMessage.set(null);
    this.loginForm.reset();
    this.registrationForm.reset();
  }

  login() {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.errorMessage.set(null);
    this.isLoading.set(true);

    const { email, password } = this.loginForm.getRawValue();

    if (!email || !password) {
      this.errorMessage.set('Email and password are required');
      return;
    }
    this.authService.login({ email, password }).subscribe({
      next: () => {
        this.isLoading.set(false);
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(err);
        console.log("Error while logging in ", err.error.error);
      },
      complete: () =>{
        console.log("Logged in successfully!");
      }
    });
  }
  register() {
    if (this.registrationForm.invalid) {
      this.registrationForm.markAllAsTouched();
      return;
    }

    this.errorMessage.set(null);
    this.isLoading.set(true);

    const { full_name, email, password } = this.registrationForm.getRawValue();

    if (!full_name || !email || !password) {
      this.errorMessage.set('Full name, Email and password are required');
      return;
    }
    this.authService.register({ full_name, email, password }).subscribe({
      next: () => {
        this.isLoading.set(false);
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(err);
        console.log("Error while registering ", err.error.error);
      },
      complete: () =>{
        console.log("Registered successfully!");
      }
    });
  }
}

import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable, signal } from '@angular/core';
import { SystemHealth, TokenResponse, UserProfile } from '../models/auth.models';
import { Observable, tap } from 'rxjs';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class Auth {
  private baseUrl = '/api/v1/auth/';
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly TOKEN_KEY = 'forecaster_access_token';

  readonly currentUser = signal<UserProfile | null>(null);
  readonly token = signal<string | null>(localStorage.getItem(this.TOKEN_KEY));
  readonly isAuthenticated = computed(() => !!this.token());

  constructor() {
    if (this.token()) {
      this.fetchProfile().subscribe({
        error: () => this.logout(),
      });
    }
  }

  fetchProfile(): Observable<UserProfile> {
    return this.http
      .get<UserProfile>(this.baseUrl + 'me')
      .pipe(tap((user) => this.currentUser.set(user)));
  }

  register(payload: {
    email: string;
    password: string;
    full_name?: string;
  }): Observable<UserProfile> {
    return this.http.post<UserProfile>(this.baseUrl + 'register', payload);
  }

  login(payload: { email: string; password: string }): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(this.baseUrl + 'login', payload).pipe(
      tap((res) => {
        localStorage.setItem(this.TOKEN_KEY, res.access_token);
        this.token.set(res.access_token);
        this.fetchProfile().subscribe();
      }),
    );
  }

  logout() {
    localStorage.clear();
    this.currentUser.set(null);
    this.token.set(null);
    this.router.navigate(['/auth']);
  }

  checkHealth(): Observable<SystemHealth> {
    return this.http.get<SystemHealth>('/health');
  }
}

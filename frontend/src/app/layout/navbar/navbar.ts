import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Auth } from '../../core/auth/auth';
import { SystemHealth } from '../../core/models/auth.models';

@Component({
  selector: 'app-navbar',
  imports: [CommonModule],
  templateUrl: './navbar.html',
  styles: ``,
})
export class Navbar implements OnInit {
  readonly authService = inject(Auth);
  readonly health = signal<SystemHealth | null>(null);

  ngOnInit(): void {
    this.authService.checkHealth().subscribe({
      next: (res) => this.health.set(res),
      error: () => this.health.set(null),
    });
  }
}

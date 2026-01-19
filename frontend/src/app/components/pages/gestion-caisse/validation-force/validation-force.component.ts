import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { ApiService } from '../../../../services/api.service';

@Component({
  selector: 'app-validation-force',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './validation-force.component.html',
  styleUrl: './validation-force.component.scss'
})
export class ValidationForceComponent implements OnInit {
  private apiService = inject(ApiService);

  caisses = signal<any[]>([]);
  loading = signal<boolean>(true);
  message = signal<string | null>(null);

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.message.set(null);
    this.apiService.getCaisses({ limit: 50 }).subscribe({
      next: (res) => {
        this.caisses.set((res?.items || []).filter((c: any) => c.etat === 'ouverte'));
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.message.set('Impossible de charger les caisses');
      }
    });
  }

  forcerFermeture(caisse: any): void {
    this.apiService.fermerCaisse(caisse.id, 'Forçage de fin de journée').subscribe({
      next: () => {
        this.message.set(`Caisse ${caisse.code} clôturée.`);
        this.refresh();
      },
      error: (err) => {
        this.message.set(err?.error?.detail || 'Erreur lors du forçage');
      }
    });
  }
}


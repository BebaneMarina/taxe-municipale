import { Component, EventEmitter, Output, OnInit, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';
import { CollecteurCreate, CollecteurUpdate, Collecteur } from '../../../../interfaces/collecteur.interface';

@Component({
  selector: 'app-create-collecteur',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-collecteur.component.html',
  styleUrl: './create-collecteur.component.scss'
})
export class CreateCollecteurComponent implements OnInit {
  @Input() collecteur: Collecteur | null = null;
  @Output() collecteurCreated = new EventEmitter<void>();
  
  private apiService = inject(ApiService);
  
  loading: boolean = false;
  error: string = '';
  isEditMode: boolean = false;
  
  // Form data
  formData: CollecteurCreate = {
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    matricule: '',
    zone_id: undefined,
    heure_cloture: undefined
  };

  ngOnInit(): void {
    if (this.collecteur) {
      this.isEditMode = true;
      this.formData = {
        nom: this.collecteur.nom || '',
        prenom: this.collecteur.prenom || '',
        email: this.collecteur.email || '',
        telephone: this.collecteur.telephone || '',
        matricule: this.collecteur.matricule || '',
        zone_id: undefined,
        heure_cloture: undefined
      };
    }
  }

  onSubmit(): void {
    this.error = '';
    
    // Validation
    if (!this.formData.nom || !this.formData.prenom) {
      this.error = 'Le nom et le prénom sont obligatoires';
      return;
    }
    
    if (!this.formData.email) {
      this.error = 'L\'email est obligatoire';
      return;
    }
    
    if (!this.formData.telephone) {
      this.error = 'Le téléphone est obligatoire';
      return;
    }

    if (!this.formData.matricule) {
      this.error = 'Le matricule est obligatoire';
      return;
    }

    this.loading = true;
    
    if (this.isEditMode && this.collecteur) {
      // Mise à jour
      const updateData: CollecteurUpdate = {
        nom: this.formData.nom,
        prenom: this.formData.prenom,
        email: this.formData.email,
        telephone: this.formData.telephone,
        zone_id: this.formData.zone_id,
        heure_cloture: this.formData.heure_cloture
      };
      
      this.apiService.updateCollecteur(this.collecteur.id, updateData).subscribe({
        next: () => {
          this.loading = false;
          this.collecteurCreated.emit();
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 'Erreur lors de la mise à jour du collecteur';
        }
      });
    } else {
      // Création
      this.apiService.createCollecteur(this.formData).subscribe({
        next: () => {
          this.loading = false;
          this.resetForm();
          this.collecteurCreated.emit();
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 'Erreur lors de la création du collecteur';
        }
      });
    }
  }

  resetForm(): void {
    this.formData = {
      nom: '',
      prenom: '',
      email: '',
      telephone: '',
      matricule: '',
      zone_id: undefined,
      heure_cloture: undefined
    };
    this.error = '';
  }
}


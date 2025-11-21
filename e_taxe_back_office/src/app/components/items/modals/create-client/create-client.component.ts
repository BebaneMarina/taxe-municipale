import { Component, EventEmitter, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';
import { ContribuableCreate } from '../../../../interfaces/contribuable.interface';
import { Zone } from '../../../../interfaces/zone.interface';
import { Quartier } from '../../../../interfaces/quartier.interface';
import { TypeContribuable } from '../../../../interfaces/type-contribuable.interface';
import { Collecteur } from '../../../../interfaces/collecteur.interface';

@Component({
  selector: 'app-create-client',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-client.component.html',
  styleUrl: './create-client.component.scss'
})
export class CreateClientComponent implements OnInit {
  @Output() clientCreated = new EventEmitter<void>();
  
  private apiService = inject(ApiService);
  
  activeEmail: boolean = false;
  loading: boolean = false;
  error: string = '';
  
  // Form data
  formData: ContribuableCreate = {
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    type_contribuable_id: 0,
    quartier_id: 0,
    collecteur_id: 0,
    adresse: '',
    nom_activite: '',
    photo_url: '',
    numero_identification: '',
    latitude: undefined,
    longitude: undefined,
    actif: true
  };

  // Photo upload
  selectedPhoto: File | null = null;
  photoPreview: string | null = null;

  // Géolocalisation
  geolocationStatus: 'idle' | 'loading' | 'success' | 'error' = 'idle';
  geolocationError: string = '';
  canGetLocation: boolean = false;
  
  // Options
  zones: Zone[] = [];
  quartiers: Quartier[] = [];
  typesContribuables: TypeContribuable[] = [];
  collecteurs: Collecteur[] = [];
  selectedZoneId: number | null = null;

  ngOnInit(): void {
    this.loadOptions();
    this.checkGeolocationSupport();
  }

  checkGeolocationSupport(): void {
    this.canGetLocation = 'geolocation' in navigator;
  }

  getCurrentLocation(): void {
    if (!this.canGetLocation) {
      this.geolocationError = 'La géolocalisation n\'est pas supportée par votre navigateur';
      return;
    }

    this.geolocationStatus = 'loading';
    this.geolocationError = '';

    navigator.geolocation.getCurrentPosition(
      (position) => {
        this.formData.latitude = position.coords.latitude;
        this.formData.longitude = position.coords.longitude;
        this.geolocationStatus = 'success';
        this.geolocationError = '';
        
        // Réinitialiser le statut après 3 secondes
        setTimeout(() => {
          if (this.geolocationStatus === 'success') {
            this.geolocationStatus = 'idle';
          }
        }, 3000);
      },
      (error) => {
        this.geolocationStatus = 'error';
        switch(error.code) {
          case error.PERMISSION_DENIED:
            this.geolocationError = 'Permission de géolocalisation refusée';
            break;
          case error.POSITION_UNAVAILABLE:
            this.geolocationError = 'Position indisponible';
            break;
          case error.TIMEOUT:
            this.geolocationError = 'Délai d\'attente dépassé';
            break;
          default:
            this.geolocationError = 'Erreur de géolocalisation';
            break;
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  }

  clearLocation(): void {
    this.formData.latitude = undefined;
    this.formData.longitude = undefined;
    this.geolocationStatus = 'idle';
    this.geolocationError = '';
  }

  onPhotoSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedPhoto = input.files[0];
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.photoPreview = e.target.result;
      };
      reader.readAsDataURL(this.selectedPhoto);
    }
  }

  removePhoto(): void {
    this.selectedPhoto = null;
    this.photoPreview = null;
    this.formData.photo_url = '';
    const input = document.getElementById('photo') as HTMLInputElement;
    if (input) {
      input.value = '';
    }
  }

  loadOptions(): void {
    // Charger les zones
    this.apiService.getZones(true).subscribe({
      next: (data) => this.zones = data,
      error: (err) => console.error('Erreur chargement zones:', err)
    });

    // Charger les types de contribuables
    this.apiService.getTypesContribuables(true).subscribe({
      next: (data) => this.typesContribuables = data,
      error: (err) => console.error('Erreur chargement types:', err)
    });

    // Charger les collecteurs actifs
    this.apiService.getCollecteurs({ actif: true, limit: 1000 }).subscribe({
      next: (data) => this.collecteurs = data,
      error: (err) => console.error('Erreur chargement collecteurs:', err)
    });
  }

  onZoneChange(zoneId: number): void {
    this.selectedZoneId = zoneId;
    this.formData.quartier_id = 0;
    this.apiService.getQuartiers(zoneId, true).subscribe({
      next: (data) => this.quartiers = data,
      error: (err) => console.error('Erreur chargement quartiers:', err)
    });
  }

  onToggleActiveEmail(active: boolean): void {
    this.activeEmail = active;
    if (!active) {
      this.formData.email = '';
    }
  }

  onSubmit(): void {
    this.error = '';
    
    // Validation
    if (!this.formData.nom || !this.formData.telephone) {
      this.error = 'Le nom et le téléphone sont obligatoires';
      return;
    }
    
    if (!this.formData.adresse || this.formData.adresse.trim() === '') {
      this.error = 'L\'adresse complète est obligatoire';
      return;
    }
    
    if (!this.formData.type_contribuable_id || !this.formData.quartier_id || !this.formData.collecteur_id) {
      this.error = 'Veuillez sélectionner le type, le quartier et le collecteur';
      return;
    }

    this.loading = true;
    
    // Préparer les données
    const data: any = {
      nom: this.formData.nom,
      prenom: this.formData.prenom || undefined,
      telephone: this.formData.telephone,
      type_contribuable_id: this.formData.type_contribuable_id,
      quartier_id: this.formData.quartier_id,
      collecteur_id: this.formData.collecteur_id,
      adresse: this.formData.adresse || undefined,
      numero_identification: this.formData.numero_identification || undefined,
      actif: this.formData.actif
    };
    
    if (this.activeEmail && this.formData.email) {
      data.email = this.formData.email;
    }

    // Ajouter les coordonnées GPS si disponibles
    if (this.formData.latitude !== undefined && this.formData.longitude !== undefined) {
      data.latitude = this.formData.latitude;
      data.longitude = this.formData.longitude;
    }

    // Ajouter nom_activite si fourni
    if (this.formData.nom_activite) {
      data.nom_activite = this.formData.nom_activite;
    }

    // Upload photo si sélectionnée
    if (this.selectedPhoto) {
      this.apiService.uploadPhoto(this.selectedPhoto).subscribe({
        next: (uploadResponse) => {
          // Construire l'URL complète
          const apiBaseUrl = 'http://localhost:8000'; // TODO: utiliser environment.apiUrl
          data.photo_url = uploadResponse.url.startsWith('http') 
            ? uploadResponse.url 
            : `${apiBaseUrl}${uploadResponse.url}`;
          // Continuer avec la création du contribuable
          this.createContribuableWithData(data);
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 'Erreur lors de l\'upload de la photo';
          console.error('Erreur upload photo:', err);
        }
      });
      return; // Sortir, la création se fera dans le callback
    }

    // Si pas de photo, créer directement
    this.createContribuableWithData(data);
  }

  private createContribuableWithData(data: any): void {
    this.apiService.createContribuable(data).subscribe({
      next: () => {
        this.loading = false;
        this.clientCreated.emit();
        this.resetForm();
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Erreur lors de la création du contribuable';
        console.error('Erreur création contribuable:', err);
      }
    });
  }

  resetForm(): void {
    this.formData = {
      nom: '',
      prenom: '',
      email: '',
      telephone: '',
      type_contribuable_id: 0,
      quartier_id: 0,
      collecteur_id: 0,
      adresse: '',
      nom_activite: '',
      photo_url: '',
      numero_identification: '',
      latitude: undefined,
      longitude: undefined,
      actif: true
    };
    this.selectedZoneId = null;
    this.quartiers = [];
    this.error = '';
    this.geolocationStatus = 'idle';
    this.geolocationError = '';
    this.removePhoto();
  }
}

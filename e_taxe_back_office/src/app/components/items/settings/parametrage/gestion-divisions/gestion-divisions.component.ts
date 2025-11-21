import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../../services/api.service';
import { ModalComponent } from '../../../../items/modal/modal.component';
import { Ville, Commune, Arrondissement, Quartier, VilleCreate, CommuneCreate, ArrondissementCreate, QuartierCreate } from '../../../../../interfaces/parametrage.interface';

@Component({
  selector: 'app-gestion-divisions',
  standalone: true,
  imports: [CommonModule, FormsModule, ModalComponent],
  templateUrl: './gestion-divisions.component.html',
  styleUrl: './gestion-divisions.component.scss'
})
export class GestionDivisionsComponent implements OnInit {
  private apiService = inject(ApiService);
  
  // Données
  villes: Ville[] = [];
  communes: Commune[] = [];
  arrondissements: Arrondissement[] = [];
  quartiers: Quartier[] = [];
  
  loading: boolean = true;
  activeTab: 'villes' | 'communes' | 'arrondissements' | 'quartiers' = 'villes';
  
  // Modals
  activeModalVille: boolean = false;
  activeModalCommune: boolean = false;
  activeModalArrondissement: boolean = false;
  activeModalQuartier: boolean = false;
  
  // Sélectionnées pour l'édition
  selectedVille: Ville | null = null;
  selectedCommune: Commune | null = null;
  selectedArrondissement: Arrondissement | null = null;
  selectedQuartier: Quartier | null = null;
  
  // Formulaires
  villeForm: VilleCreate = { nom: '', code: '', description: '', pays: 'Gabon', actif: true };
  communeForm: CommuneCreate = { nom: '', code: '', ville_id: 0, description: '', actif: true };
  arrondissementForm: ArrondissementCreate = { nom: '', code: '', commune_id: 0, description: '', actif: true };
  quartierForm: QuartierCreate = { nom: '', code: '', arrondissement_id: 0, description: '', actif: true };

  // Données gabonaises pré-définies
  villesGabon = [
    { nom: 'Libreville', code: 'LBV', description: 'Capitale du Gabon' },
    { nom: 'Port-Gentil', code: 'POG', description: 'Ville économique' },
    { nom: 'Franceville', code: 'FRV', description: 'Ville du Haut-Ogooué' },
    { nom: 'Oyem', code: 'OYM', description: 'Ville du Woleu-Ntem' },
    { nom: 'Moanda', code: 'MND', description: 'Ville minière' },
    { nom: 'Mouila', code: 'MLA', description: 'Ville de la Ngounié' },
    { nom: 'Tchibanga', code: 'TCB', description: 'Ville de la Nyanga' },
    { nom: 'Koulamoutou', code: 'KLM', description: 'Ville de l\'Ogooué-Lolo' },
    { nom: 'Makokou', code: 'MKK', description: 'Ville de l\'Ogooué-Ivindo' },
    { nom: 'Lambaréné', code: 'LBR', description: 'Ville de Moyen-Ogooué' }
  ];

  // Communes de Libreville
  communesLibreville = [
    { nom: 'Commune de Libreville', code: 'LBV-COM', description: 'Commune principale' },
    { nom: 'Commune d\'Akanda', code: 'AKD', description: 'Commune au nord-est' },
    { nom: 'Commune d\'Owendo', code: 'OWD', description: 'Commune industrielle' },
    { nom: 'Commune de Ntoum', code: 'NTM', description: 'Commune périphérique' }
  ];

  ngOnInit(): void {
    this.loadVilles();
  }

  setTab(tab: 'villes' | 'communes' | 'arrondissements' | 'quartiers'): void {
    this.activeTab = tab;
    switch(tab) {
      case 'villes':
        this.loadVilles();
        break;
      case 'communes':
        this.loadCommunes();
        break;
      case 'arrondissements':
        this.loadArrondissements();
        break;
      case 'quartiers':
        this.loadQuartiers();
        break;
    }
  }

  // ==================== VILLES ====================
  loadVilles(): void {
    this.loading = true;
    this.apiService.getVilles({ actif: true }).subscribe({
      next: (data: Ville[]) => {
        this.villes = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des villes:', err);
        // Si l'endpoint n'existe pas encore, utiliser les données par défaut
        this.villes = this.villesGabon.map((v, i) => ({
          id: i + 1,
          nom: v.nom,
          code: v.code,
          description: v.description,
          pays: 'Gabon',
          actif: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }));
        this.loading = false;
      }
    });
  }

  openCreateVilleModal(): void {
    this.selectedVille = null;
    this.villeForm = { nom: '', code: '', description: '', pays: 'Gabon', actif: true };
    this.activeModalVille = true;
  }

  openEditVilleModal(ville: Ville): void {
    this.selectedVille = ville;
    this.villeForm = {
      nom: ville.nom,
      code: ville.code,
      description: ville.description || '',
      pays: ville.pays || 'Gabon',
      actif: ville.actif
    };
    this.activeModalVille = true;
  }

  saveVille(): void {
    if (!this.villeForm.nom || !this.villeForm.code) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (this.selectedVille) {
      this.apiService.updateVille(this.selectedVille.id, this.villeForm).subscribe({
        next: () => {
          this.loadVilles();
          this.activeModalVille = false;
        },
        error: (err) => {
          console.error('Erreur lors de la mise à jour:', err);
          alert('Erreur lors de la mise à jour de la ville');
        }
      });
    } else {
      this.apiService.createVille(this.villeForm).subscribe({
        next: () => {
          this.loadVilles();
          this.activeModalVille = false;
        },
        error: (err) => {
          console.error('Erreur lors de la création:', err);
          alert('Erreur lors de la création de la ville');
        }
      });
    }
  }

  deleteVille(ville: Ville): void {
    if (confirm(`Êtes-vous sûr de vouloir supprimer la ville "${ville.nom}" ?`)) {
      this.apiService.deleteVille(ville.id).subscribe({
        next: () => {
          this.loadVilles();
        },
        error: (err) => {
          console.error('Erreur lors de la suppression:', err);
          alert('Erreur lors de la suppression de la ville');
        }
      });
    }
  }

  // ==================== COMMUNES ====================
  loadCommunes(villeId?: number): void {
    this.loading = true;
    this.apiService.getCommunes(villeId, { actif: true }).subscribe({
      next: (data: Commune[]) => {
        this.communes = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des communes:', err);
        this.loading = false;
      }
    });
  }

  openCreateCommuneModal(villeId?: number): void {
    this.selectedCommune = null;
    this.communeForm = { nom: '', code: '', ville_id: villeId || 0, description: '', actif: true };
    this.activeModalCommune = true;
  }

  openEditCommuneModal(commune: Commune): void {
    this.selectedCommune = commune;
    this.communeForm = {
      nom: commune.nom,
      code: commune.code,
      ville_id: commune.ville_id,
      description: commune.description || '',
      actif: commune.actif
    };
    this.activeModalCommune = true;
  }

  saveCommune(): void {
    if (!this.communeForm.nom || !this.communeForm.code || !this.communeForm.ville_id) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (this.selectedCommune) {
      this.apiService.updateCommune(this.selectedCommune.id, this.communeForm).subscribe({
        next: () => {
          this.loadCommunes();
          this.activeModalCommune = false;
        },
        error: (err) => {
          console.error('Erreur lors de la mise à jour:', err);
          alert('Erreur lors de la mise à jour de la commune');
        }
      });
    } else {
      this.apiService.createCommune(this.communeForm).subscribe({
        next: () => {
          this.loadCommunes();
          this.activeModalCommune = false;
        },
        error: (err) => {
          console.error('Erreur lors de la création:', err);
          alert('Erreur lors de la création de la commune');
        }
      });
    }
  }

  deleteCommune(commune: Commune): void {
    if (confirm(`Êtes-vous sûr de vouloir supprimer la commune "${commune.nom}" ?`)) {
      this.apiService.deleteCommune(commune.id).subscribe({
        next: () => {
          this.loadCommunes();
        },
        error: (err) => {
          console.error('Erreur lors de la suppression:', err);
          alert('Erreur lors de la suppression de la commune');
        }
      });
    }
  }

  // ==================== ARRONDISSEMENTS ====================
  loadArrondissements(communeId?: number): void {
    this.loading = true;
    this.apiService.getArrondissements(communeId, { actif: true }).subscribe({
      next: (data: Arrondissement[]) => {
        this.arrondissements = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des arrondissements:', err);
        this.loading = false;
      }
    });
  }

  openCreateArrondissementModal(communeId?: number): void {
    this.selectedArrondissement = null;
    this.arrondissementForm = { nom: '', code: '', commune_id: communeId || 0, description: '', actif: true };
    this.activeModalArrondissement = true;
  }

  openEditArrondissementModal(arrondissement: Arrondissement): void {
    this.selectedArrondissement = arrondissement;
    this.arrondissementForm = {
      nom: arrondissement.nom,
      code: arrondissement.code,
      commune_id: arrondissement.commune_id,
      description: arrondissement.description || '',
      actif: arrondissement.actif
    };
    this.activeModalArrondissement = true;
  }

  saveArrondissement(): void {
    if (!this.arrondissementForm.nom || !this.arrondissementForm.code || !this.arrondissementForm.commune_id) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (this.selectedArrondissement) {
      this.apiService.updateArrondissement(this.selectedArrondissement.id, this.arrondissementForm).subscribe({
        next: () => {
          this.loadArrondissements();
          this.activeModalArrondissement = false;
        },
        error: (err) => {
          console.error('Erreur lors de la mise à jour:', err);
          alert('Erreur lors de la mise à jour de l\'arrondissement');
        }
      });
    } else {
      this.apiService.createArrondissement(this.arrondissementForm).subscribe({
        next: () => {
          this.loadArrondissements();
          this.activeModalArrondissement = false;
        },
        error: (err) => {
          console.error('Erreur lors de la création:', err);
          alert('Erreur lors de la création de l\'arrondissement');
        }
      });
    }
  }

  deleteArrondissement(arrondissement: Arrondissement): void {
    if (confirm(`Êtes-vous sûr de vouloir supprimer l'arrondissement "${arrondissement.nom}" ?`)) {
      this.apiService.deleteArrondissement(arrondissement.id).subscribe({
        next: () => {
          this.loadArrondissements();
        },
        error: (err) => {
          console.error('Erreur lors de la suppression:', err);
          alert('Erreur lors de la suppression de l\'arrondissement');
        }
      });
    }
  }

  // ==================== QUARTIERS ====================
  loadQuartiers(arrondissementId?: number): void {
    this.loading = true;
    // Utiliser l'API existante des quartiers avec support pour arrondissement
    // Pour l'instant, récupérer tous les quartiers actifs
    // L'arrondissement_id sera géré dans une future version de l'API
    this.apiService.getQuartiers(undefined, true, arrondissementId ? { arrondissement_id: arrondissementId } : undefined).subscribe({
      next: (data: Quartier[]) => {
        // Filtrer par arrondissement_id côté client si nécessaire
        if (arrondissementId && data) {
          this.quartiers = data.filter(q => q.arrondissement_id === arrondissementId);
        } else {
          this.quartiers = data;
        }
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des quartiers:', err);
        this.loading = false;
      }
    });
  }

  openCreateQuartierModal(arrondissementId?: number): void {
    this.selectedQuartier = null;
    this.quartierForm = { nom: '', code: '', arrondissement_id: arrondissementId || 0, description: '', actif: true };
    this.activeModalQuartier = true;
  }

  openEditQuartierModal(quartier: Quartier): void {
    this.selectedQuartier = quartier;
    this.quartierForm = {
      nom: quartier.nom,
      code: quartier.code,
      arrondissement_id: quartier.arrondissement_id || 0,
      description: quartier.description || '',
      actif: quartier.actif
    };
    this.activeModalQuartier = true;
  }

  saveQuartier(): void {
    if (!this.quartierForm.nom || !this.quartierForm.code) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (this.selectedQuartier) {
      this.apiService.updateQuartier(this.selectedQuartier.id, this.quartierForm).subscribe({
        next: () => {
          this.loadQuartiers();
          this.activeModalQuartier = false;
        },
        error: (err) => {
          console.error('Erreur lors de la mise à jour:', err);
          alert('Erreur lors de la mise à jour du quartier');
        }
      });
    } else {
      this.apiService.createQuartier(this.quartierForm).subscribe({
        next: () => {
          this.loadQuartiers();
          this.activeModalQuartier = false;
        },
        error: (err) => {
          console.error('Erreur lors de la création:', err);
          alert('Erreur lors de la création du quartier');
        }
      });
    }
  }

  deleteQuartier(quartier: Quartier): void {
    if (confirm(`Êtes-vous sûr de vouloir supprimer le quartier "${quartier.nom}" ?`)) {
      this.apiService.deleteQuartier(quartier.id).subscribe({
        next: () => {
          this.loadQuartiers();
        },
        error: (err) => {
          console.error('Erreur lors de la suppression:', err);
          alert('Erreur lors de la suppression du quartier');
        }
      });
    }
  }

  // Helpers
  getVilleName(villeId: number): string {
    const ville = this.villes.find(v => v.id === villeId);
    return ville ? ville.nom : 'N/A';
  }

  getCommuneName(communeId: number): string {
    const commune = this.communes.find(c => c.id === communeId);
    return commune ? commune.nom : 'N/A';
  }

  getArrondissementName(arrondissementId: number): string {
    const arrondissement = this.arrondissements.find(a => a.id === arrondissementId);
    return arrondissement ? arrondissement.nom : 'N/A';
  }
}


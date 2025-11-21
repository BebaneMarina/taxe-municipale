import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../../services/api.service';
import { ModalComponent } from '../../../../items/modal/modal.component';
import { SecteurActivite, SecteurActiviteCreate } from '../../../../../interfaces/parametrage.interface';

@Component({
  selector: 'app-gestion-secteurs',
  standalone: true,
  imports: [CommonModule, FormsModule, ModalComponent],
  templateUrl: './gestion-secteurs.component.html',
  styleUrl: './gestion-secteurs.component.scss'
})
export class GestionSecteursComponent implements OnInit {
  private apiService = inject(ApiService);
  
  secteurs: SecteurActivite[] = [];
  loading: boolean = true;
  searchTerm: string = '';
  activeModal: boolean = false;
  selectedSecteur: SecteurActivite | null = null;
  isEditMode: boolean = false;

  // Formulaire
  secteurForm: SecteurActiviteCreate = {
    nom: '',
    code: '',
    description: '',
    actif: true
  };

  // Secteurs d'activité gabonais pré-définis
  secteursGabon = [
    { nom: 'Commerce général', code: 'COM-GEN', description: 'Commerce de biens divers' },
    { nom: 'Restauration', code: 'REST', description: 'Restaurants, cafés, snacks' },
    { nom: 'Hôtellerie', code: 'HOTEL', description: 'Hôtels, auberges, hébergement' },
    { nom: 'Transport', code: 'TRANS', description: 'Transport de personnes et marchandises' },
    { nom: 'Bâtiment et travaux publics', code: 'BTP', description: 'Construction, travaux' },
    { nom: 'Services financiers', code: 'FIN', description: 'Banques, microfinance, assurance' },
    { nom: 'Artisanat', code: 'ART', description: 'Artisanat local' },
    { nom: 'Santé', code: 'SANTE', description: 'Cliniques, pharmacies, cabinets médicaux' },
    { nom: 'Éducation', code: 'EDUC', description: 'Écoles, formation' },
    { nom: 'Industrie', code: 'IND', description: 'Transformation, production' },
    { nom: 'Agriculture et élevage', code: 'AGRI', description: 'Production agricole et élevage' },
    { nom: 'Pêche', code: 'PECHE', description: 'Pêche artisanale et commerciale' },
    { nom: 'Services publics', code: 'PUB', description: 'Services administratifs' },
    { nom: 'Télécommunications', code: 'TELECOM', description: 'Téléphonie, internet' },
    { nom: 'Énergie', code: 'ENERGIE', description: 'Production et distribution d\'énergie' },
    { nom: 'Mines', code: 'MINES', description: 'Exploitation minière' },
    { nom: 'Services aux entreprises', code: 'SERV-ENT', description: 'Conseil, services professionnels' },
    { nom: 'Médias et communication', code: 'MEDIA', description: 'Presse, radio, télévision' },
    { nom: 'Loisirs et divertissement', code: 'LOISIRS', description: 'Divertissement, sports, culture' },
    { nom: 'Commerce de détail', code: 'RET', description: 'Vente au détail' },
    { nom: 'Commerce de gros', code: 'GROS', description: 'Vente en gros' },
    { nom: 'Automobile', code: 'AUTO', description: 'Vente et réparation de véhicules' },
    { nom: 'Immobilier', code: 'IMMO', description: 'Agence immobilière, location' },
    { nom: 'Services à la personne', code: 'SERV-PERS', description: 'Services domestiques, ménage' },
    { nom: 'Autre', code: 'AUTRE', description: 'Autres activités non classées' }
  ];

  ngOnInit(): void {
    this.loadSecteurs();
  }

  loadSecteurs(): void {
    this.loading = true;
    this.apiService.getSecteursActivite({ actif: true }).subscribe({
      next: (data: SecteurActivite[]) => {
        this.secteurs = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des secteurs:', err);
        // Si l'endpoint n'existe pas encore, utiliser les données par défaut
        this.secteurs = this.secteursGabon.map((s, i) => ({
          id: i + 1,
          nom: s.nom,
          code: s.code,
          description: s.description,
          actif: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }));
        this.loading = false;
      }
    });
  }

  onSearch(): void {
    if (!this.searchTerm) {
      this.loadSecteurs();
      return;
    }
    this.secteurs = this.secteurs.filter(s =>
      s.nom.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
      s.code.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
      s.description?.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  openCreateModal(): void {
    this.isEditMode = false;
    this.selectedSecteur = null;
    this.resetForm();
    this.activeModal = true;
  }

  openEditModal(secteur: SecteurActivite): void {
    this.isEditMode = true;
    this.selectedSecteur = secteur;
    this.secteurForm = {
      nom: secteur.nom,
      code: secteur.code,
      description: secteur.description || '',
      actif: secteur.actif
    };
    this.activeModal = true;
  }

  closeModal(): void {
    this.activeModal = false;
    this.resetForm();
  }

  resetForm(): void {
    this.secteurForm = {
      nom: '',
      code: '',
      description: '',
      actif: true
    };
  }

  saveSecteur(): void {
    if (!this.secteurForm.nom || !this.secteurForm.code) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (this.isEditMode && this.selectedSecteur) {
      this.apiService.updateSecteurActivite(this.selectedSecteur.id, this.secteurForm).subscribe({
        next: () => {
          this.loadSecteurs();
          this.closeModal();
        },
        error: (err) => {
          console.error('Erreur lors de la mise à jour:', err);
          alert('Erreur lors de la mise à jour du secteur d\'activité');
        }
      });
    } else {
      this.apiService.createSecteurActivite(this.secteurForm).subscribe({
        next: () => {
          this.loadSecteurs();
          this.closeModal();
        },
        error: (err) => {
          console.error('Erreur lors de la création:', err);
          alert('Erreur lors de la création du secteur d\'activité');
        }
      });
    }
  }

  deleteSecteur(secteur: SecteurActivite): void {
    if (confirm(`Êtes-vous sûr de vouloir supprimer le secteur "${secteur.nom}" ?`)) {
      this.apiService.deleteSecteurActivite(secteur.id).subscribe({
        next: () => {
          this.loadSecteurs();
        },
        error: (err) => {
          console.error('Erreur lors de la suppression:', err);
          alert('Erreur lors de la suppression du secteur d\'activité');
        }
      });
    }
  }

  toggleActif(secteur: SecteurActivite): void {
    this.apiService.updateSecteurActivite(secteur.id, { actif: !secteur.actif }).subscribe({
      next: () => {
        this.loadSecteurs();
      },
      error: (err) => {
        console.error('Erreur lors de la mise à jour:', err);
      }
    });
  }

  // Charger les données par défaut du Gabon
  loadDefaultData(): void {
    if (confirm('Voulez-vous charger les secteurs d\'activité pré-définis pour le Gabon ?')) {
      let count = 0;
      this.secteursGabon.forEach(secteur => {
        this.apiService.createSecteurActivite(secteur).subscribe({
          next: () => {
            count++;
            if (count === this.secteursGabon.length) {
              this.loadSecteurs();
              alert('Secteurs d\'activité chargés avec succès !');
            }
          },
          error: (err) => {
            console.error('Erreur lors de la création:', err);
          }
        });
      });
    }
  }
}


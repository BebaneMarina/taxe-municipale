import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../../services/api.service';
import { ModalComponent } from '../../../../items/modal/modal.component';
import { Role } from '../../../../../interfaces/parametrage.interface';

@Component({
  selector: 'app-gestion-roles',
  standalone: true,
  imports: [CommonModule, FormsModule, ModalComponent],
  templateUrl: './gestion-roles.component.html',
  styleUrl: './gestion-roles.component.scss'
})
export class GestionRolesComponent implements OnInit {
  private apiService = inject(ApiService);
  
  roles: Role[] = [];
  loading: boolean = true;
  searchTerm: string = '';
  activeModal: boolean = false;
  selectedRole: Role | null = null;
  isEditMode: boolean = false;

  // Formulaire
  roleForm = {
    nom: '',
    code: '',
    description: '',
    permissions: [] as string[],
    actif: true
  };

  // Rôles disponibles dans le système
  availableRoles = [
    { value: 'admin', label: 'Administrateur', code: 'admin' },
    { value: 'agent_back_office', label: 'Agent Back Office', code: 'agent_back_office' },
    { value: 'agent_front_office', label: 'Agent Front Office', code: 'agent_front_office' },
    { value: 'controleur_interne', label: 'Contrôleur Interne', code: 'controleur_interne' },
    { value: 'collecteur', label: 'Collecteur', code: 'collecteur' }
  ];

  // Permissions disponibles
  availablePermissions = [
    { value: 'read_users', label: 'Lire les utilisateurs' },
    { value: 'create_users', label: 'Créer des utilisateurs' },
    { value: 'update_users', label: 'Modifier les utilisateurs' },
    { value: 'delete_users', label: 'Supprimer des utilisateurs' },
    { value: 'read_contribuables', label: 'Lire les contribuables' },
    { value: 'create_contribuables', label: 'Créer des contribuables' },
    { value: 'update_contribuables', label: 'Modifier les contribuables' },
    { value: 'delete_contribuables', label: 'Supprimer les contribuables' },
    { value: 'read_collectes', label: 'Lire les collectes' },
    { value: 'create_collectes', label: 'Créer des collectes' },
    { value: 'update_collectes', label: 'Modifier les collectes' },
    { value: 'read_taxes', label: 'Lire les taxes' },
    { value: 'create_taxes', label: 'Créer des taxes' },
    { value: 'update_taxes', label: 'Modifier les taxes' },
    { value: 'delete_taxes', label: 'Supprimer les taxes' },
    { value: 'read_rapports', label: 'Lire les rapports' },
    { value: 'manage_parametrage', label: 'Gérer le paramétrage' }
  ];

  ngOnInit(): void {
    this.loadRoles();
  }

  loadRoles(): void {
    this.loading = true;
    this.apiService.getRoles({ actif: true }).subscribe({
      next: (data: Role[]) => {
        this.roles = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des rôles:', err);
        this.loading = false;
      }
    });
  }

  onSearch(): void {
    // Filtrer les rôles localement
    if (!this.searchTerm) {
      this.loadRoles();
      return;
    }
    this.roles = this.roles.filter(r =>
      r.nom.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
      r.code.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  openCreateModal(): void {
    this.isEditMode = false;
    this.selectedRole = null;
    this.resetForm();
    this.activeModal = true;
  }

  openEditModal(role: Role): void {
    this.isEditMode = true;
    this.selectedRole = role;
    this.roleForm = {
      nom: role.nom,
      code: role.code,
      description: role.description || '',
      permissions: [...role.permissions],
      actif: role.actif
    };
    this.activeModal = true;
  }

  closeModal(): void {
    this.activeModal = false;
    this.resetForm();
  }

  resetForm(): void {
    this.roleForm = {
      nom: '',
      code: '',
      description: '',
      permissions: [],
      actif: true
    };
  }

  togglePermission(permission: string): void {
    const index = this.roleForm.permissions.indexOf(permission);
    if (index > -1) {
      this.roleForm.permissions.splice(index, 1);
    } else {
      this.roleForm.permissions.push(permission);
    }
  }

  isPermissionSelected(permission: string): boolean {
    return this.roleForm.permissions.includes(permission);
  }

  onRoleNameChange(): void {
    // Mettre à jour automatiquement le code quand le nom change
    const selectedRole = this.availableRoles.find(r => r.value === this.roleForm.nom);
    if (selectedRole && !this.isEditMode) {
      this.roleForm.code = selectedRole.code;
    }
  }

  allPermissionsSelected(): boolean {
    return this.availablePermissions.length > 0 && 
           this.availablePermissions.every(perm => this.isPermissionSelected(perm.value));
  }

  toggleAllPermissions(): void {
    if (this.allPermissionsSelected()) {
      // Désélectionner toutes les permissions
      this.roleForm.permissions = [];
    } else {
      // Sélectionner toutes les permissions
      this.roleForm.permissions = this.availablePermissions.map(perm => perm.value);
    }
  }

  saveRole(): void {
    if (!this.roleForm.nom || !this.roleForm.code) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (this.isEditMode && this.selectedRole) {
      this.apiService.updateRole(this.selectedRole.id, this.roleForm).subscribe({
        next: () => {
          this.loadRoles();
          this.closeModal();
        },
        error: (err) => {
          console.error('Erreur lors de la mise à jour du rôle:', err);
          alert('Erreur lors de la mise à jour du rôle');
        }
      });
    } else {
      this.apiService.createRole(this.roleForm).subscribe({
        next: () => {
          this.loadRoles();
          this.closeModal();
        },
        error: (err) => {
          console.error('Erreur lors de la création du rôle:', err);
          alert('Erreur lors de la création du rôle');
        }
      });
    }
  }

  deleteRole(role: Role): void {
    if (confirm(`Êtes-vous sûr de vouloir supprimer le rôle "${role.nom}" ?`)) {
      this.apiService.deleteRole(role.id).subscribe({
        next: () => {
          this.loadRoles();
        },
        error: (err) => {
          console.error('Erreur lors de la suppression du rôle:', err);
          alert('Erreur lors de la suppression du rôle');
        }
      });
    }
  }

  toggleActif(role: Role): void {
    this.apiService.updateRole(role.id, { actif: !role.actif }).subscribe({
      next: () => {
        this.loadRoles();
      },
      error: (err) => {
        console.error('Erreur lors de la mise à jour:', err);
      }
    });
  }
}


import { Routes } from '@angular/router';
import { DashboardComponent } from './components/pages/dashboard/dashboard.component';
import { TransactionsComponent } from './components/pages/transactions/transactions.component';
import { BalanceComponent } from './components/pages/balance/balance.component';
import { ClientsComponent } from './components/pages/clients/clients.component';
import { SettingsComponent } from './components/pages/settings/settings.component';
import { LayoutComponent } from './components/pages/layout/layout.component';
import { GestionCollecteursComponent } from './components/pages/gestion-collecteurs/gestion-collecteurs.component';
import { AdministrationsComponent } from './components/pages/administrations/administrations.component';
import { LoginComponent } from './components/pages/login/login.component';
import { AuthGuard } from './guards/auth.guard';
import { RoleGuard } from './guards/role.guard';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent,
    title: 'Connexion'
  },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [AuthGuard],
    children: [
      {
        path: '',
        component: DashboardComponent,
        title: 'Tableau de bord'
      },
      {
        path: 'transactions',
        component: TransactionsComponent,
        title: 'Historiques'
      },
      {
        path: 'balance',
        component: BalanceComponent,
        title: 'Gestion des clients'
      },
      {
        path: 'clients',
        component: ClientsComponent,
        title: 'Gestion des contribuables'
      },
      {
        path: 'taxes',
        loadComponent: () => import('./components/pages/taxes/taxes.component').then(m => m.TaxesComponent),
        title: 'Gestion des taxes'
      },
      {
        path: 'collecteurs',
        component: GestionCollecteursComponent,
        title: 'Gestion des collecteurs',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'agent_back_office'] }
      },
      {
        path: 'administration',
        component: AdministrationsComponent,
        title: 'Administrations',
        canActivate: [RoleGuard],
        data: { roles: ['admin'] }
      },
      {
        path: 'settings',
        component: SettingsComponent,
        title: 'Paramètres'
      },
      {
        path: 'rapports',
        loadComponent: () => import('./components/pages/rapports/rapports.component').then(m => m.RapportsComponent),
        title: 'Rapports et Statistiques'
      },
      {
        path: 'cartographie',
        loadComponent: () => import('./components/pages/cartographie/cartographie.component').then(m => m.CartographieComponent),
        title: 'Cartographie'
      },
      {
        path: 'relances',
        loadComponent: () => import('./components/pages/relances/relances.component').then(m => m.RelancesComponent),
        title: 'Gestion des Relances'
      },
      {
        path: 'impayes',
        loadComponent: () => import('./components/pages/impayes/impayes.component').then(m => m.ImpayesComponent),
        title: 'Gestion des Impayés'
      },
      {
        path: 'travaux',
        loadComponent: () => import('./components/pages/travaux/travaux.component').then(m => m.TravauxComponent),
        title: 'Travaux du jour',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'agent_back_office'] }
      },
      {
        path: 'commissions',
        loadComponent: () => import('./components/pages/commissions/commissions.component').then(m => m.CommissionsComponent),
        title: 'Fichiers de commissions',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'agent_back_office'] }
      },
      {
        path: 'gestion-caisse/parametrage-coupures',
        loadComponent: () => import('./components/pages/gestion-caisse/parametrage-coupures/parametrage-coupures.component')
          .then(m => m.ParametrageCoupuresComponent),
        title: 'Paramétrage des coupures',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'agent_back_office'] }
      },
      {
        path: 'gestion-caisse/parametrage',
        loadComponent: () => import('./components/pages/caisses/caisses.component').then(m => m.ParametrageCaisseComponent),
        title: 'Paramétrage des caisses',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'agent_back_office'] }
      },
      {
        path: 'gestion-caisse/affectation',
        loadComponent: () => import('./components/pages/gestion-caisse/affectation-caisse/affectation-caisse.component')
          .then(m => m.AffectationCaisseComponent),
        title: 'Affectation des caisses',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'agent_back_office'] }
      },
      {
        path: 'gestion-caisse/validation-force',
        loadComponent: () => import('./components/pages/gestion-caisse/validation-force/validation-force.component')
          .then(m => m.ValidationForceComponent),
        title: 'Validation forçage arrêté',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'agent_back_office'] }
      },
      {
        path: 'gestion-caisse/approvisionnement',
        loadComponent: () => import('./components/pages/gestion-caisse/approvisionnement-caisse/approvisionnement-caisse.component')
          .then(m => m.ApprovisionnementCaisseComponent),
        title: 'Approvisionnement caisse',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'agent_back_office'] }
      },
      {
        path: 'gestion-caisse/journal',
        loadComponent: () => import('./components/pages/gestion-caisse/journal-caisse/journal-caisse.component')
          .then(m => m.JournalCaisseComponent),
        title: 'Journal de caisse',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'agent_back_office'] }
      }
    ]
  },
  {
    path: 'client/paiement',
    loadComponent: () => import('./components/pages/paiement-client/paiement-client.component').then(m => m.PaiementClientComponent),
    title: 'Paiement des Taxes'
  },
  {
    path: '**',
    redirectTo: ''
  }
];

import { Routes } from '@angular/router';

import { HomePageComponent } from './features/home/home-page.component';
import { AnalyzerPageComponent } from './features/analyzer/analyzer-page.component';

export const routes: Routes = [
  {
    path: '',
    component: HomePageComponent,
    title: 'GitHub Analyzer',
  },
  {
    path: 'analyzer',
    component: AnalyzerPageComponent,
    title: 'Analyzer | GitHub Analyzer',
  },
  {
    path: '**',
    redirectTo: '',
  },
];

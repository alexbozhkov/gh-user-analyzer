import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

import { AnalysisRepositoryViewModel } from '../../../core/models/github.models';

@Component({
  selector: 'app-repository-list',
  standalone: true,
  templateUrl: './repository-list.component.html',
  styleUrl: './repository-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RepositoryListComponent {
  @Input() repositories: AnalysisRepositoryViewModel[] = [];
}

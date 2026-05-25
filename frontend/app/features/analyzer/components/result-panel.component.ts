import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { NbCardModule, NbSpinnerModule } from '@nebular/theme';

import { AnalysisResultViewModel } from '../../../core/models/github.models';
import { RepositoryListComponent } from './repository-list.component';

@Component({
  selector: 'app-result-panel',
  standalone: true,
  imports: [NbCardModule, NbSpinnerModule, RepositoryListComponent],
  templateUrl: './result-panel.component.html',
  styleUrl: './result-panel.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResultPanelComponent {
  @Input({ required: true }) title!: string;
  @Input({ required: true }) subtitle!: string;
  @Input({ required: true }) flavor!: 'rest' | 'graphql';
  @Input({ required: true }) tokenRequirement!: string;
  @Input({ required: true }) requestProfile!: string;
  @Input() loading = false;
  @Input() error = '';
  @Input() data: AnalysisResultViewModel | null = null;

  formatResetTimestamp(reset: number | null): string | null {
    if (reset === null) {
      return null;
    }

    return new Date(reset * 1000).toLocaleString();
  }
}

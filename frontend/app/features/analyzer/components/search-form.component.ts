import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NbButtonModule, NbCardModule, NbInputModule } from '@nebular/theme';

@Component({
  selector: 'app-search-form',
  standalone: true,
  imports: [FormsModule, NbButtonModule, NbCardModule, NbInputModule],
  templateUrl: './search-form.component.html',
  styleUrl: './search-form.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SearchFormComponent {
  @Input() username = '';
  @Input() token = '';
  @Input() tokenRequired = false;

  @Output() readonly usernameChange = new EventEmitter<string>();
  @Output() readonly tokenChange = new EventEmitter<string>();
  @Output() readonly searchRest = new EventEmitter<void>();
  @Output() readonly searchGraphql = new EventEmitter<void>();
}

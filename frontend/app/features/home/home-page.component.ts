import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NbButtonModule, NbCardModule } from '@nebular/theme';

@Component({
  selector: 'app-home-page',
  standalone: true,
  imports: [RouterLink, NbButtonModule, NbCardModule],
  templateUrl: './home-page.component.html',
  styleUrl: './home-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomePageComponent {}

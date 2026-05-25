import { importProvidersFrom } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideNoopAnimations } from '@angular/platform-browser/animations';
import { NbThemeModule } from '@nebular/theme';

import { HomePageComponent } from './home-page.component';

describe('HomePageComponent', () => {
  let fixture: ComponentFixture<HomePageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomePageComponent],
      providers: [
        provideRouter([]),
        provideNoopAnimations(),
        importProvidersFrom(NbThemeModule.forRoot({ name: 'cosmic' })),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HomePageComponent);
    fixture.detectChanges();
  });

  it('renders the landing title', () => {
    const title = fixture.nativeElement.querySelector('h1');

    expect(title?.textContent).toContain('Compare REST and GraphQL');
  });

  it('links the primary call to action to the analyzer route', () => {
    const links = Array.from(fixture.nativeElement.querySelectorAll('a')) as HTMLAnchorElement[];
    const link = links.find((anchor) => anchor.textContent?.includes('Open Analyzer'));

    expect(link?.textContent).toContain('Open Analyzer');
  });
});

import { importProvidersFrom } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { provideNoopAnimations } from '@angular/platform-browser/animations';
import { NbThemeModule } from '@nebular/theme';

import { AnalyzerPageComponent } from './analyzer-page.component';
import { GithubService } from '../../core/services/github.service';

describe('AnalyzerPageComponent', () => {
  let fixture: ComponentFixture<AnalyzerPageComponent>;
  let component: AnalyzerPageComponent;
  let githubService: jasmine.SpyObj<GithubService>;

  beforeEach(async () => {
    githubService = jasmine.createSpyObj<GithubService>('GithubService', ['getUserSummary', 'getUserSummaryRest']);

    await TestBed.configureTestingModule({
      imports: [AnalyzerPageComponent],
      providers: [
        provideNoopAnimations(),
        importProvidersFrom(NbThemeModule.forRoot({ name: 'cosmic' })),
        { provide: GithubService, useValue: githubService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AnalyzerPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('shows a validation error when username is missing', () => {
    component.searchGraphql();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Please enter a GitHub username.');
  });

  it('requires a token for the GraphQL solution', () => {
    component.githubUsername = 'octocat';
    component.githubToken = '';
    component.searchGraphql();

    expect(githubService.getUserSummary).not.toHaveBeenCalled();
    expect(component.graphqlError).toBe('Please enter a GitHub token for the GraphQL solution.');
  });

  it('loads GraphQL data after search', () => {
    githubService.getUserSummary.and.returnValue(
      of({
        data: {
          userSummary: {
            username: 'octocat',
            followersCount: 2,
            mostUsedLanguage: 'Python',
            technologies: ['Docker', 'Python'],
            messages: [],
            cached: false,
            authUsed: true,
            rateLimitLimit: 5000,
            rateLimitRemaining: 4999,
            rateLimitUsed: 1,
            rateLimitReset: 1779471697,
            rateLimitResource: 'graphql',
            repositories: [],
          },
        },
      }),
    );

    component.githubUsername = 'octocat';
    component.githubToken = 'token';
    component.searchGraphql();
    fixture.detectChanges();

    expect(githubService.getUserSummary).toHaveBeenCalledWith('octocat', 'token');
    expect(component.graphqlData?.username).toBe('octocat');
    expect(fixture.nativeElement.textContent).toContain('4999 remaining / 5000 total');
  });

  it('loads REST data after search', () => {
    githubService.getUserSummaryRest.and.returnValue(
      of({
        username: 'octocat',
        followers_count: 2,
        most_used_language: 'Python',
        technologies: ['Docker', 'Python'],
        messages: [],
        metadata: {
          cached: false,
          auth_used: false,
          rate_limit: {
            limit: 60,
            remaining: 58,
            used: 2,
            reset: 1779471697,
            resource: 'core',
          },
        },
        repositories: [],
      }),
    );

    component.githubUsername = 'octocat';
    component.githubToken = 'token';
    component.searchRest();
    fixture.detectChanges();

    expect(githubService.getUserSummaryRest).toHaveBeenCalledWith('octocat', 'token');
    expect(component.restData?.username).toBe('octocat');
    expect(fixture.nativeElement.textContent).toContain('58 remaining / 60 total');
  });
});

import { HttpErrorResponse } from '@angular/common/http';
import { importProvidersFrom } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
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

    expect(githubService.getUserSummaryRest).toHaveBeenCalledWith('octocat');
    expect(component.restData?.username).toBe('octocat');
    expect(fixture.nativeElement.textContent).toContain('58 remaining / 60 total');
  });

  it('shows a validation error when username is missing for REST', () => {
    component.searchRest();
    fixture.detectChanges();

    expect(component.restError).toBe('Please enter a GitHub username.');
    expect(githubService.getUserSummaryRest).not.toHaveBeenCalled();
  });

  it('handles REST HTTP error', () => {
    githubService.getUserSummaryRest.and.returnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            error: { detail: 'REST API error' },
            status: 404,
          }),
      ),
    );

    component.githubUsername = 'octocat';
    component.searchRest();
    fixture.detectChanges();

    expect(component.restError).toBe('REST API error');
  });

  it('handles REST HTTP error with no detail', () => {
    githubService.getUserSummaryRest.and.returnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            status: 500,
          }),
      ),
    );

    component.githubUsername = 'octocat';
    component.searchRest();
    fixture.detectChanges();

    expect(component.restError).toBe('REST request failed.');
  });

  it('handles GraphQL response with errors', () => {
    githubService.getUserSummary.and.returnValue(
      of({
        errors: [{ message: 'GitHub user does not exist.' }],
      } as any),
    );

    component.githubUsername = 'octocat';
    component.githubToken = 'token';
    component.searchGraphql();
    fixture.detectChanges();

    expect(component.graphqlError).toBe('GitHub user does not exist.');
    expect(component.graphqlData).toBeNull();
  });

  it('handles GraphQL HTTP error', () => {
    githubService.getUserSummary.and.returnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            error: { detail: 'Internal server error' },
            status: 500,
          }),
      ),
    );

    component.githubUsername = 'octocat';
    component.githubToken = 'token';
    component.searchGraphql();
    fixture.detectChanges();

    expect(component.graphqlError).toBe('Internal server error');
  });

  it('handles GraphQL returning null data', () => {
    githubService.getUserSummary.and.returnValue(
      of({
        data: { userSummary: null },
      } as any),
    );

    component.githubUsername = 'octocat';
    component.githubToken = 'token';
    component.searchGraphql();
    fixture.detectChanges();

    expect(component.graphqlError).toBe('No data was returned from the GraphQL endpoint.');
    expect(component.graphqlData).toBeNull();
  });

  it('updates username via updateUsername', () => {
    component.updateUsername('newuser');
    expect(component.githubUsername).toBe('newuser');
  });

  it('updates token via updateToken and clears tokenRequired flag', () => {
    component.graphqlTokenRequired = true;
    component.updateToken('newtoken');
    expect(component.githubToken).toBe('newtoken');
    expect(component.graphqlTokenRequired).toBe(false);
  });

  it('does not clear graphqlTokenRequired when token is blank', () => {
    component.graphqlTokenRequired = true;
    component.updateToken('   ');
    expect(component.graphqlTokenRequired).toBe(true);
  });
});

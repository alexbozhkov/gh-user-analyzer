import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { of } from 'rxjs';

import { AppComponent } from './app.component';
import { GithubService } from './github.service';

describe('AppComponent', () => {
  let fixture: ComponentFixture<AppComponent>;
  let component: AppComponent;
  let githubService: jasmine.SpyObj<GithubService>;

  beforeEach(async () => {
    githubService = jasmine.createSpyObj<GithubService>('GithubService', ['getUserSummary', 'getUserSummaryRest']);

    await TestBed.configureTestingModule({
      declarations: [AppComponent],
      imports: [FormsModule, HttpClientTestingModule],
      providers: [{ provide: GithubService, useValue: githubService }],
    }).compileComponents();

    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('renders the page title', () => {
    const title = fixture.nativeElement.querySelector('h1');

    expect(title?.textContent).toContain('Github Analyzer');
  });

  it('shows a validation error when username is missing', () => {
    component.searchGraphql();
    fixture.detectChanges();

    const messages = Array.from(fixture.nativeElement.querySelectorAll('p')) as HTMLParagraphElement[];
    const message = messages.find((paragraph) => paragraph.textContent?.includes('Please enter a GitHub username.'));

    expect(message?.textContent).toContain('Please enter a GitHub username.');
  });

  it('requires a token for the GraphQL solution', () => {
    component.githubUsername = 'octocat';
    component.githubToken = '';
    component.searchGraphql();

    expect(githubService.getUserSummary).not.toHaveBeenCalled();
    expect(component.graphqlError).toBe('Please enter a GitHub token for the GraphQL solution.');
  });

  it('loads GraphQL data after search', () => {
    githubService.getUserSummary.and.returnValue(of({
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
        }
      }
    }));

    component.githubUsername = 'octocat';
    component.githubToken = 'token';
    component.searchGraphql();

    expect(githubService.getUserSummary).toHaveBeenCalledWith('octocat', 'token');
    expect(component.graphqlData?.username).toBe('octocat');
    expect(component.graphqlError).toBe('');
  });

  it('loads REST data after search', () => {
    githubService.getUserSummaryRest.and.returnValue(of({
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
    }));

    component.githubUsername = 'octocat';
    component.githubToken = 'token';
    component.searchRest();

    expect(githubService.getUserSummaryRest).toHaveBeenCalledWith('octocat', 'token');
    expect(component.restData?.username).toBe('octocat');
    expect(component.restError).toBe('');
  });
});

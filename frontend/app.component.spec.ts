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
    githubService = jasmine.createSpyObj<GithubService>('GithubService', ['getUserSummary']);

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
    component.search();
    fixture.detectChanges();

    const message = fixture.nativeElement.querySelector('p');

    expect(message?.textContent).toContain('Please enter a GitHub username.');
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
          repositories: [],
        }
      }
    }));

    component.githubUsername = 'octocat';
    component.githubToken = 'token';
    component.search();

    expect(githubService.getUserSummary).toHaveBeenCalledWith('octocat', 'token');
    expect(component.data?.username).toBe('octocat');
    expect(component.error).toBe('');
  });
});

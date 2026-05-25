import { ChangeDetectionStrategy, ChangeDetectorRef, Component } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { NbCardModule } from '@nebular/theme';

import {
  AnalysisRepositoryViewModel,
  AnalysisResultViewModel,
  GraphqlUserSummary,
  RestRateLimitMetadata,
  RestUserSummary,
} from '../../core/models/github.models';
import { GithubService } from '../../core/services/github.service';
import { SearchFormComponent } from './components/search-form.component';
import { ResultPanelComponent } from './components/result-panel.component';

@Component({
  selector: 'app-analyzer-page',
  standalone: true,
  imports: [NbCardModule, SearchFormComponent, ResultPanelComponent],
  templateUrl: './analyzer-page.component.html',
  styleUrl: './analyzer-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AnalyzerPageComponent {
  githubUsername = '';
  githubToken = '';
  graphqlData: AnalysisResultViewModel | null = null;
  graphqlError = '';
  graphqlLoading = false;
  restData: AnalysisResultViewModel | null = null;
  restError = '';
  restLoading = false;

  constructor(
    private readonly githubService: GithubService,
    private readonly cdr: ChangeDetectorRef,
  ) {}

  updateUsername(value: string): void {
    this.githubUsername = value;
  }

  updateToken(value: string): void {
    this.githubToken = value;
  }

  searchGraphql(): void {
    const username = this.githubUsername.trim();

    if (!username) {
      this.graphqlError = 'Please enter a GitHub username.';
      this.graphqlData = null;
      return;
    }

    if (!this.githubToken.trim()) {
      this.graphqlError = 'Please enter a GitHub token for the GraphQL solution.';
      this.graphqlData = null;
      return;
    }

    this.graphqlLoading = true;
    this.graphqlError = '';
    this.graphqlData = null;

    this.githubService.getUserSummary(username, this.githubToken).subscribe({
      next: (response) => {
        this.graphqlLoading = false;

        if (response.errors?.length) {
          this.graphqlError = response.errors.map((error) => error.message).join(', ');
          this.cdr.markForCheck();
          return;
        }

        const summary = response.data?.userSummary ?? null;
        this.graphqlData = summary ? this.normalizeGraphqlSummary(summary) : null;

        if (!this.graphqlData) {
          this.graphqlError = 'No data was returned from the GraphQL endpoint.';
        }

        this.cdr.markForCheck();
      },
      error: (error: HttpErrorResponse) => {
        this.graphqlLoading = false;
        this.graphqlError = error.error?.detail ?? 'GraphQL request failed.';
        this.cdr.markForCheck();
      },
    });
  }

  searchRest(): void {
    const username = this.githubUsername.trim();

    if (!username) {
      this.restError = 'Please enter a GitHub username.';
      this.restData = null;
      return;
    }

    this.restLoading = true;
    this.restError = '';
    this.restData = null;

    this.githubService.getUserSummaryRest(username, this.githubToken).subscribe({
      next: (response) => {
        this.restLoading = false;
        this.restData = this.normalizeRestSummary(response);
        this.cdr.markForCheck();
      },
      error: (error: HttpErrorResponse) => {
        this.restLoading = false;
        this.restError = error.error?.detail ?? 'REST request failed.';
        this.cdr.markForCheck();
      },
    });
  }

  private normalizeGraphqlSummary(summary: GraphqlUserSummary): AnalysisResultViewModel {
    return {
      username: summary.username,
      followersCount: summary.followersCount,
      repositories: summary.repositories.map((repository) => this.normalizeRepository(repository)),
      mostUsedLanguage: summary.mostUsedLanguage,
      technologies: summary.technologies,
      messages: summary.messages,
      cached: summary.cached,
      authUsed: summary.authUsed,
      rateLimit: {
        limit: summary.rateLimitLimit,
        remaining: summary.rateLimitRemaining,
        used: summary.rateLimitUsed,
        reset: summary.rateLimitReset,
        resource: summary.rateLimitResource,
      },
    };
  }

  private normalizeRestSummary(summary: RestUserSummary): AnalysisResultViewModel {
    const rateLimit = summary.metadata?.rate_limit ?? this.emptyRateLimit();

    return {
      username: summary.username,
      followersCount: summary.followers_count,
      repositories: summary.repositories.map((repository) =>
        this.normalizeRepository({
          name: repository.name,
          url: repository.url,
          primaryLanguage: repository.primary_language,
          technologies: repository.technologies,
        }),
      ),
      mostUsedLanguage: summary.most_used_language,
      technologies: summary.technologies,
      messages: summary.messages,
      cached: summary.metadata?.cached ?? false,
      authUsed: summary.metadata?.auth_used ?? false,
      rateLimit,
    };
  }

  private normalizeRepository(repository: AnalysisRepositoryViewModel): AnalysisRepositoryViewModel {
    return {
      name: repository.name,
      url: repository.url,
      primaryLanguage: repository.primaryLanguage,
      technologies: repository.technologies,
    };
  }

  private emptyRateLimit(): RestRateLimitMetadata {
    return {
      limit: null,
      remaining: null,
      used: null,
      reset: null,
      resource: null,
    };
  }
}

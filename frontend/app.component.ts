import { Component } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { GithubService, GraphqlUserSummary, RestUserSummary } from './github.service';


@Component({
    selector: 'app-root',
    templateUrl: './app.component.html'
})

export class AppComponent {

    githubUsername = '';
    githubToken = '';
    graphqlData: GraphqlUserSummary | null = null;
    graphqlError = '';
    graphqlLoading = false;
    restData: RestUserSummary | null = null;
    restError = '';
    restLoading = false;

    constructor(private githubService: GithubService) {}

    searchGraphql() {
        if (!this.githubUsername.trim()) {
            this.graphqlError = 'Please enter a GitHub username.';
            this.graphqlData = null;
            return;
        }

        this.graphqlLoading = true;
        this.graphqlError = '';
        this.graphqlData = null;

        this.githubService.getUserSummary(this.githubUsername.trim(), this.githubToken).subscribe({
            next: (response) => {
                this.graphqlLoading = false;
                if (response.errors?.length) {
                    this.graphqlError = response.errors.map((error) => error.message).join(', ');
                    return;
                }
                this.graphqlData = response.data?.userSummary ?? null;
                if (!this.graphqlData) {
                    this.graphqlError = 'No data was returned from the GraphQL endpoint.';
                }
            },
            error: (error: HttpErrorResponse) => {
                this.graphqlLoading = false;
                this.graphqlError = error.error?.detail ?? 'GraphQL request failed.';
            }
        });
    }

    searchRest() {
        if (!this.githubUsername.trim()) {
            this.restError = 'Please enter a GitHub username.';
            this.restData = null;
            return;
        }

        this.restLoading = true;
        this.restError = '';
        this.restData = null;

        this.githubService.getUserSummaryRest(this.githubUsername.trim(), this.githubToken).subscribe({
            next: (response) => {
                this.restLoading = false;
                this.restData = response;
            },
            error: (error: HttpErrorResponse) => {
                this.restLoading = false;
                this.restError = error.error?.detail ?? 'REST request failed.';
            }
        });
    }

}

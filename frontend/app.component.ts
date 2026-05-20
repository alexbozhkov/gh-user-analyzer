import { Component } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { GithubService, GraphqlUserSummary } from './github.service';


@Component({
    selector: 'app-root',
    templateUrl: './app.component.html'
})

export class AppComponent {

    githubUsername = '';
    githubToken = '';
    data: GraphqlUserSummary | null = null;
    error = '';
    loading = false;

    constructor(private githubService: GithubService) {}

    search() {
        if (!this.githubUsername.trim()) {
            this.error = 'Please enter a GitHub username.';
            this.data = null;
            return;
        }

        this.loading = true;
        this.error = '';
        this.data = null;

        this.githubService.getUserSummary(this.githubUsername.trim(), this.githubToken).subscribe({
            next: (response) => {
                this.loading = false;
                if (response.errors?.length) {
                    this.error = response.errors.map((error) => error.message).join(', ');
                    return;
                }
                this.data = response.data?.userSummary ?? null;
                if (!this.data) {
                    this.error = 'No data was returned from the GraphQL endpoint.';
                }
            },
            error: (error: HttpErrorResponse) => {
                this.loading = false;
                this.error = error.error?.detail ?? 'Request failed.';
            }
        });
    }

}

import { Component } from '@angular/core';
import { GithubService } from './github.service';


@Component({
    selector: 'app-root',
    templateUrl: './app.component.html'
})

export class AppComponent {

    githubUsername = '';
    data: unknown = null;
    error = '';

    constructor(private githubService: GithubService) {}

    search() {
        this.error = 'Search is not wired yet.';
    }

}

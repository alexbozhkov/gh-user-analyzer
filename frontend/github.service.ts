import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


@Injectable({
    providedIn: 'root'
})

export class GithubService {

    private apiUrl = '/api/user';

    constructor(private http: HttpClient) {}

    getUser(username: string): Observable<unknown> {
        return this.http.get(`${this.apiUrl}?username=${username}`);
    }

}

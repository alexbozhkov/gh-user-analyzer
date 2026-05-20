import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';


export interface GraphqlRepository {
	name: string;
	url: string;
	primaryLanguage: string | null;
	technologies: string[];
}

export interface GraphqlUserSummary {
	username: string;
	followersCount: number;
	repositories: GraphqlRepository[];
	mostUsedLanguage: string | null;
	technologies: string[];
	messages: string[];
}

export interface GraphqlResponse<T> {
	data?: T;
	errors?: Array<{ message: string }>;
}


@Injectable({
	providedIn: 'root'
})

export class GithubService {

	private apiUrl = '/graphql';

	constructor(private http: HttpClient) { }

	getUserSummary(username: string, token: string): Observable<GraphqlResponse<{ userSummary: GraphqlUserSummary }>> {
		const headers = token.trim()
			? new HttpHeaders({ 'X-GitHub-Token': token.trim() })
			: undefined;

		return this.http.post<GraphqlResponse<{ userSummary: GraphqlUserSummary }>>(
			this.apiUrl,
			{
				query: `query($username: String!) {
                    userSummary(username: $username) {
                        username
                        followersCount
                        mostUsedLanguage
                        technologies
                        messages
                        repositories {
                            name
                            url
                            primaryLanguage
                            technologies
                        }
                    }
                }`,
				variables: { username }
			},
			{ headers }
		);
	}

}

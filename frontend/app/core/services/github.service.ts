import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

import { GraphqlResponse, GraphqlUserSummary, RestUserSummary } from '../models/github.models';

@Injectable({
  providedIn: 'root',
})
export class GithubService {
  private readonly graphqlUrl = '/graphql';
  private readonly restUrl = '/users';

  constructor(private readonly http: HttpClient) {}

  getUserSummary(username: string, token: string): Observable<GraphqlResponse<{ userSummary: GraphqlUserSummary }>> {
    const trimmedToken = token.trim();
    const headers = trimmedToken ? new HttpHeaders({ 'X-GitHub-Token': trimmedToken }) : undefined;

    return this.http.post<GraphqlResponse<{ userSummary: GraphqlUserSummary }>>(
      this.graphqlUrl,
      {
        query: `query($username: String!) {
          userSummary(username: $username) {
            username
            followersCount
            mostUsedLanguage
            technologies
            messages
            cached
            authUsed
            rateLimitLimit
            rateLimitRemaining
            rateLimitUsed
            rateLimitReset
            rateLimitResource
            repositories {
              name
              url
              primaryLanguage
              technologies
            }
          }
        }`,
        variables: { username },
      },
      { headers },
    );
  }

  getUserSummaryRest(username: string): Observable<RestUserSummary> {
    return this.http.get<RestUserSummary>(this.restUrl, {
      params: { username },
    });
  }
}

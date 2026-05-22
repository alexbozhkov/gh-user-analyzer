USER_ANALYSIS_QUERY = """
query UserAnalysis($login: String!, $after: String) {
  user(login: $login) {
    login
    followers {
      totalCount
    }
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        url
        primaryLanguage {
          name
        }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          nodes {
            name
          }
        }
      }
    }
  }
}
"""

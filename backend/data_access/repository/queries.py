USER_ANALYSIS_QUERY = """
query UserAnalysis($login: String!) {
  user(login: $login) {
    login
    followers {
      totalCount
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      totalCount
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

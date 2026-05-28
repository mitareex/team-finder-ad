from users.validators import check_github_domain


class GitHubCleanMixin:
    """Mixin for validation GitHub Urls"""
    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url')
        if github_url:
            check_github_domain(github_url)
        return github_url

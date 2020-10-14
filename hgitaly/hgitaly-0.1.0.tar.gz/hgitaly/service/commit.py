# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging

from ..stub.commit_pb2 import (
    CommitIsAncestorRequest,
    CommitIsAncestorResponse,
    CommitsBetweenRequest,
    CommitsBetweenResponse,
    CountCommitsRequest,
    CountCommitsResponse,
    FindCommitRequest,
    FindCommitResponse,
)
from ..stub.commit_pb2_grpc import CommitServiceServicer

from .. import message
from ..revision import gitlab_revision_changeset
from ..servicer import HGitalyServicer
from ..util import chunked

logger = logging.getLogger(__name__)


class CommitServicer(CommitServiceServicer, HGitalyServicer):

    def CommitIsAncestor(self,
                         request: CommitIsAncestorRequest,
                         context) -> CommitIsAncestorResponse:
        repo = self.load_repo(request.repository, context)
        # TODO status.Errorf(codes.InvalidArgument, "Bad Request
        # (empty ancestor sha)") and same for child
        ancestor = repo[request.ancestor_id]
        child = repo[request.child_id]
        return CommitIsAncestorResponse(value=ancestor.isancestorof(child))

    def TreeEntry(self, request, context):
        raise NotImplementedError(
            "TreeEntry method not directly relevant for Mercurial"
        )  # pragma no cover

    def CommitsBetween(self,
                       request: CommitsBetweenRequest,
                       context) -> CommitsBetweenResponse:
        """Stream chunks of commits "between" two GitLab revisions.

        One may believe the meaning of "between" to be based on DAG ranges,
        but actually, what the Gitaly reference Golang implementation does is
        ``git log --reverse FROM..TO``, which is indeed commonly used to obtain
        exclusive DAG ranges (would be `FROM::TO - FROM`) but gitrevisions(1)
        actually says:
           you can ask for commits that are reachable
           from r2 excluding those that are reachable from r1 by ^r1 r2
           and it can be written as r1..r2.

        So the true Mercurial equivalent revset is actually `TO % FROM`,
        which is quite different if FROM is not an ancestor of TO.

        Sadly, we happen to know `%` to be less efficient than DAG ranges.

        TODO: assuming the most common use case is indeed to obtain DAG ranges,
        (for which GitLab would actually have to check ancestry first), maybe
        introduce a direct call for DAG ranges later.
        """
        repo = self.load_repo(request.repository, context)
        # TODO ERROR. Treat the case when rev_from or rev_to doesn't exist
        # (and is there a default value btw? In Git CLI that would be HEAD)
        rev_from = gitlab_revision_changeset(repo, getattr(request, 'from'))
        rev_to = gitlab_revision_changeset(repo, request.to)
        revs = repo.revs('only(%s, %s)', rev_to, rev_from)
        for chunk in chunked(revs):
            yield CommitsBetweenResponse(
                commits=(message.commit(repo[rev]) for rev in chunk))

    def CountCommits(self,
                     request: CountCommitsRequest,
                     context) -> CountCommitsResponse:
        raise NotImplementedError(
            "Implementation tracking issue: hgitaly#7"
        )  # pragma no cover

    def FindCommit(self,
                   request: FindCommitRequest, context) -> FindCommitResponse:
        repo = self.load_repo(request.repository, context)
        revision = request.revision
        logger.debug("FindCommit revision=%r", revision)
        ctx = gitlab_revision_changeset(repo, revision)

        commit = None if ctx is None else message.commit(ctx)
        return FindCommitResponse(commit=commit)

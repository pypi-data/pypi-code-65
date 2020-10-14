# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import time
from mercurial import (
    pycompat,
)
from hgext3rd.heptapod.branch import set_default_gitlab_branch

from hgitaly.tests.common import (
    make_empty_repo,
    make_tree_shaped_repo,
)

from hgitaly.stub.commit_pb2 import (
    CommitIsAncestorRequest,
    CommitsBetweenRequest,
    FindCommitRequest,
)
from hgitaly.stub.commit_pb2_grpc import CommitServiceStub


def test_is_ancestor(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    _, grpc_repo, changesets = make_tree_shaped_repo(server_repos_root)

    def is_ancestor(key1, key2):
        resp = grpc_stub.CommitIsAncestor(
            CommitIsAncestorRequest(repository=grpc_repo,
                                    ancestor_id=changesets[key1].hex(),
                                    child_id=changesets[key2].hex(),
                                    ))
        return resp.value

    assert is_ancestor('base', 'top1')
    assert not is_ancestor('other_base', 'default')
    assert is_ancestor('default', 'default')
    assert is_ancestor('other_base', 'wild2')


# TODO test with tags. In particular they have precedence in Mercurial
# over branches
def test_find_commit(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    now = time.time()
    ctx = wrapper.write_commit('foo',
                               utc_timestamp=now,
                               user="HGitaly Test <hgitaly@heptapod.test>")
    ctx2 = wrapper.write_commit('foo',
                                parent=ctx,
                                message="Foo deux\n\nA very interesting bar")

    request = FindCommitRequest(repository=grpc_repo, revision=ctx.hex())
    response = grpc_stub.FindCommit(request)

    commit = response.commit
    assert commit is not None
    assert commit.id == ctx.hex().decode()
    assert commit.parent_ids == []
    assert commit.author.name == b"HGitaly Test"
    assert commit.author.email == b"hgitaly@heptapod.test"
    assert commit.author.date.seconds == int(now)

    request = FindCommitRequest(repository=grpc_repo, revision=ctx2.hex())
    response = grpc_stub.FindCommit(request)

    commit2 = response.commit
    assert commit2 is not None
    assert commit2.subject == b'Foo deux'
    assert commit2.body == b"Foo deux\n\nA very interesting bar"
    assert commit2.parent_ids == [ctx.hex().decode()]

    # TODO check with two parents, it'd be nice to have a helper to create
    # merge commits very quickly

    request = FindCommitRequest(repository=grpc_repo,
                                revision=b'branch/default')
    response = grpc_stub.FindCommit(request)
    assert response.commit == commit2

    # default GitLab branch not being set, it fallbacks on branch/default
    request = FindCommitRequest(repository=grpc_repo, revision=b'HEAD')
    assert response.commit == commit2

    wrapper.write_commit('animals',
                         message="in topic",
                         topic='antelope',
                         parent=ctx)
    request = FindCommitRequest(repository=grpc_repo,
                                revision=b'topic/default/antelope')
    response = grpc_stub.FindCommit(request)

    commit_top = response.commit
    assert commit_top is not None
    assert commit_top.subject == b"in topic"

    # with explicitely set GitLab branch:
    set_default_gitlab_branch(wrapper.repo, b'topic/default/antelope')
    request = FindCommitRequest(repository=grpc_repo, revision=b'HEAD')
    response = grpc_stub.FindCommit(request)
    assert response.commit == commit_top

    request = FindCommitRequest(repository=grpc_repo, revision=b'unknown')
    response = grpc_stub.FindCommit(request)
    assert not response.HasField('commit')


def test_commits_between(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    _, grpc_repo, changesets = make_tree_shaped_repo(server_repos_root)

    def do_rpc(gl_from, gl_to):
        request = CommitsBetweenRequest(repository=grpc_repo, to=gl_to)
        setattr(request, 'from', gl_from)
        resp = grpc_stub.CommitsBetween(request)
        return [pycompat.sysbytes(commit.id)
                for chunk in resp for commit in chunk.commits]

    base = changesets['base']
    top1, top2 = changesets['top1'], changesets['top2']
    assert do_rpc(base.hex(), b'topic/default/zzetop') == [
        top1.hex(), top2.hex()]

    # This is counter intuitive, check the docstring for CommitsBetween.
    # The actual expected result was checked by comparing with the reponse of
    # a reference Golang Gitaly 12.10.6 server working on conversion to Git of
    # this precise testing repo.
    assert do_rpc(b'branch/other', b'topic/default/zzetop') == [
        top1.hex(), top2.hex()]
    assert do_rpc(base.hex(), b'branch/other') == [
        changesets['other_base'].hex(), changesets['wild2'].hex()]

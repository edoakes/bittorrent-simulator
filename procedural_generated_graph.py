import json
import random
import argparse

"""
Procedural generated graph with soft connection limit of 5, max limit of 20:
 - 5000 peers, 500MB: 18 iterations
 - 1000 peers, 10GB: p50 297 iterations, p100 384 iterations (65% ~ 84% speed)
"""

parser = argparse.ArgumentParser(description='Simulate procedurally generated graph')
parser.add_argument('--peers', default=5000, type=int, help='total number of peers')
parser.add_argument('--pieces', default=125, type=int, help='total number of pieces')
parser.add_argument('--transmit-limit', default=10, type=int, help='number of pieces uploaded/downloaded per iteration')
parser.add_argument('--soft-conn-limit', default=5, type=int, help='max number of peers to connect to')
parser.add_argument('--hard-conn-limit', default=20, type=int, help='max number of peers to allow connections')

class Peer(object):
    def __init__(self, name, piece_count, transmit_limit):
        self.name = name
        self.failed_connection_attempts = 0
        self.neighbors = set()
        self.pieces = [0]*piece_count
        self.transmit_limit = transmit_limit
        self.completed = 0
        self.time = 0

        self.uploaded_current_turn = 0
        self.downloaded_current_turn = 0

    def connect(self, other):
        self.neighbors.add(other)
        other.neighbors.add(self)

    def done(self):
        return self.completed == len(self.pieces)

    def fetch_step(self, time):
        if self.done():
            return

        if self.downloaded_current_turn >= self.transmit_limit:
            return

        candidates = []
        for n in self.neighbors:
            if n.uploaded_current_turn >= self.transmit_limit:
                continue

            for i in range(0, len(self.pieces)):
                if n.uploaded_current_turn >= self.transmit_limit:
                    continue

                if n.pieces[i] == 1 and self.pieces[i] == 0:
                    candidates.append((n, i))

        if len(candidates) == 0:
            return

        c = random.choice(candidates)

        self.pieces[c[1]] = 1
        self.completed += 1
        self.downloaded_current_turn += 1
        c[0].uploaded_current_turn += 1

        if self.completed == len(self.pieces)-1:
            self.time = time
            print ('Peer %s finished downloading at time %d.' % (self.name, time))

    def fetch_cleanup(self):
        self.uploaded_current_turn = 0
        self.downloaded_current_turn = 0

    def __lt__(self, other):
        return self.name.__lt__(other.name)

class PeerManager(object):

    def __init__(self, peer_count, piece_count, transmit_limit, soft_limit, hard_limit):
        self.peers = []

        for n in range(peer_count):
            peer = Peer(str(n), piece_count, transmit_limit)
            if n > 0:
                random.shuffle(self.peers)
                for candidate in self.peers:
                    if len(candidate.neighbors) < hard_limit:
                        peer.connect(candidate)
                        if len(peer.neighbors) >= soft_limit:
                            break
                    else:
                        peer.failed_connection_attempts += 1
                        if peer.failed_connection_attempts > 50:
                            break

            self.peers.append(peer)

        self.peers.sort()
        for peer in self.peers:
            neighbors_str = ""
            for neighbor in peer.neighbors:
                neighbors_str = neighbors_str + neighbor.name + "; "
            print ('Peer %s failed %d connection attempts. Connected to peers %s' % (
                peer.name, peer.failed_connection_attempts, neighbors_str))

        # Set peer 0 to be the seeder.
        self.peers[0].pieces = [1]*piece_count
        self.peers[0].completed = len(self.peers[0].pieces)

    def start(self):
        time = 0
        while True:
            print ('current time: %d.' % time)
            time += 1

            plan = []
            for p in self.peers:
                if not p.done():
                    for j in range(0, p.transmit_limit):
                        plan.append(p)
            random.shuffle(plan)
            for p in plan:
                p.fetch_step(time)

            for p in self.peers:
                p.fetch_cleanup()

            done = True
            for p in self.peers:
                if p.completed != len(p.pieces):
                    done = False

            if done:
                break

            if time > 1000:
                break

        print ('Done. Total time: %d.' % time)


def main(args):
    peer_manager = PeerManager(args.peers, args.pieces, args.transmit_limit, args.soft_conn_limit, args.hard_conn_limit)
    peer_manager.start()

if __name__== "__main__":
     main(parser.parse_args())

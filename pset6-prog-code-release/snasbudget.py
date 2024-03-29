#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index
import math
from random import uniform

class snasbudget:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2


    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = [a_id_b for a_id_b in prev_round.bids if a_id_b[0] != self.id]

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)

        info = list(map(compute, list(range(len(clicks)))))
#        sys.stdout.write("slot info: %s\n" % info)
        return info

    # def clicks_per_position(self, t, num_slots):
    #     """
    #     From the pset, we have a closed-form expression for clicks per
    #     position given the period. This is implemented here.

    #     input: period (t), num_position
    #     output: list of clicks per position, with position i at index i - 1.
    #     """
    #     clicks_in_round_1 = round(30 * math.cos(math.pi * t / 24) + 50)
    #     return [round(.75 ** (j) * clicks_in_round_1) for j in range(num_slots)]

    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        prev_round = history.round(t-1)
        clicks = prev_round.clicks
        num_slots = max(1, len(clicks))
        
        other_bids = [a_id_b for a_id_b in prev_round.bids if a_id_b[0] != self.id]
        other_bids.append((self.id, 0)) # add back in the null bid corresponding to you
        sorted_bids = sorted(other_bids, key = lambda x: x[1], reverse = True)
        
        # if len(clicks) < num_slots:
        #     for _ in range(num_slots - len(clicks)):
        #         clicks.append(0)

        # print("CLICKS: ", clicks, "NUM_SLOTS: ", num_slots, "SORTED_BIDS: ", sorted_bids)
        utilities = [clicks[j] * (self.value - max(sorted_bids[j][1], reserve)) for j in range(num_slots)]
        # print("clicks per: ", clicks, "sorted bids is: ", sorted_bids, "t is: ", t)
        return utilities

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        clicks = prev_round.clicks
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)

        # If Not expecting to win, bid your value:
        if min_bid > self.value:
            bid = self.value
        # Elif Not going for top,
        elif slot > 0:
            # num_slots = slot + 1
            # pos = clicks
            # print("CLICKS AND SLOT ARE: ", clicks, slot, clicks[slot-1], self.value, min_bid)
            # print("SLOT IS TOO HIGH! ", "TARGET SLOT IS: ", slot, "ID IS: ", self.id, "VALUE IS: ", self.value)
            bid = self.value - (clicks[slot] / clicks[slot-1])*(self.value - min_bid)
            if bid < reserve and reserve < self.value:
                bid = reserve
            elif bid < reserve and reserve > self.value:
                bid = 0
            else:
                if t < 15:
                    round(uniform(reserve, bid))
        
        # Else, Going for top,
        else:
            # print("GOING FOR THE TOP! ", "TARGET SLOT IS: ", slot, "ID IS: ", self.id, "VALUE IS: ", self.value)
            bid = self.value
            if bid < reserve:
                bid = 0

        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)



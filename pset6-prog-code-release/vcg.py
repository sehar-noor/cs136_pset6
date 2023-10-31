#!/usr/bin/env python

import random

from gsp import GSP

class VCG:
    """
    Implements the Vickrey-Clarke-Groves mechanism for ad auctions.
    """
    @staticmethod
    def compute(slot_clicks, reserve, bids):
        """
        Given info about the setting (clicks for each slot, and reserve price),
        and bids (list of (id, bid) tuples), compute the following:
          allocation:  list of the occupant in each slot
              len(allocation) = min(len(bids), len(slot_clicks))
          per_click_payments: list of payments for each slot
              len(per_click_payments) = len(allocation)

        If any bids are below the reserve price, they are ignored.

        Returns a pair of lists (allocation, per_click_payments):
         - allocation is a list of the ids of the bidders in each slot
            (in order)
         - per_click_payments is the corresponding payments.
        """

        # The allocation is the same as GSP, so we filled that in for you...

        valid = lambda a_bid: a_bid[1] >= reserve
        valid_bids = list(filter(valid, bids))

        # shuffle first to make sure we don't have any bias for lower or
        # higher ids
        random.shuffle(valid_bids)
        valid_bids.sort(key=lambda b: b[1], reverse=True)

        num_slots = len(slot_clicks)
        allocated_bids = valid_bids[:num_slots]
        if len(allocated_bids) == 0:
            return ([], [])

        (agents, all_bids) = list(zip(*sorted(bids, key=lambda x: x[1], reverse=True)))
        (allocation, just_bids) = list(zip(*sorted(allocated_bids, key=lambda x: x[1], reverse=True)))

        # Payments function
        def total_payment(k):
            c = slot_clicks
            n = len(allocation)
            if k < n:
                without_bidder = [max(b, reserve) for b in just_bids[:k]] + [max(b, reserve) for b in just_bids[k+1:]]
                # Using max to ensure next_bid is at least the reserve
                next_bid = next(max(bid, reserve) for bid in reversed(all_bids) if bid not in without_bidder)
                without_bidder.append(next_bid)
                utility_without = sum(without_bidder[i] * c[i] for i in range(len(just_bids)))
                utility_with = sum(max(just_bids[i], reserve) * c[i] for i in range(len(just_bids)) if i != k)
                return utility_without - utility_with

        def norm(totals):
            """Normalize total payments by the clicks in each slot"""
            return [x_y[0]/x_y[1] for x_y in zip(totals, slot_clicks)]

        per_click_payments = norm(
            [total_payment(k) for k in range(len(allocation))])

        return (list(allocation), per_click_payments)

    @staticmethod
    def bid_range_for_slot(slot, slot_clicks, reserve, bids):
        """
        Compute the range of bids that would result in the bidder ending up
        in slot, given that the other bidders submit bidders.
        Returns a tuple (min_bid, max_bid).
        If slot == 0, returns None for max_bid, since it's not well defined.
        """
        # Conveniently enough, bid ranges are the same for GSP and VCG:
        return GSP.bid_range_for_slot(slot, slot_clicks, reserve, bids)

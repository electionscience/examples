import unittest


candidates = ["Squash", "Potato", "Broccoli", "Blueberry", "Strawberry", "Banana"]


class MyTestCase(unittest.TestCase):
    def test_generate_ballot(self):
        bb1 = dict(zip(candidates, [5, 5, 5, 0, 0, 0]))
        bb2 = dict(zip(candidates, [3, 5, 5, 2, 2, 2]))
        bb3 = dict(zip(candidates, [5, 5, 5, 5, 0, 0]))
        bb4 = dict(zip(candidates, [0, 0, 0, 5, 5, 4]))
        bb5 = dict(zip(candidates, [0, 0, 4, 5, 5, 5]))
        bb6 = dict(zip(candidates, [0, 0, 0, 5, 5, 3]))

        ballot1 = {
            candidates[0]: 5,
            candidates[1]: 5,
            candidates[2]: 5,
            candidates[3]: 0,
            candidates[4]: 0,
            candidates[5]: 0,
        }
        ballot2 = {
            candidates[0]: 3,
            candidates[1]: 5,
            candidates[2]: 5,
            candidates[3]: 2,
            candidates[4]: 2,
            candidates[5]: 2,
        }
        ballot3 = {
            candidates[0]: 5,
            candidates[1]: 5,
            candidates[2]: 5,
            candidates[3]: 5,
            candidates[4]: 0,
            candidates[5]: 0,
        }
        ballot4 = {
            candidates[0]: 0,
            candidates[1]: 0,
            candidates[2]: 0,
            candidates[3]: 5,
            candidates[4]: 5,
            candidates[5]: 4,
        }
        ballot5 = {
            candidates[0]: 0,
            candidates[1]: 0,
            candidates[2]: 4,
            candidates[3]: 5,
            candidates[4]: 5,
            candidates[5]: 5,
        }
        ballot6 = {
            candidates[0]: 0,
            candidates[1]: 0,
            candidates[2]: 0,
            candidates[3]: 5,
            candidates[4]: 5,
            candidates[5]: 3,
        }

        self.assertEqual(bb1, ballot1)
        self.assertEqual(bb2, ballot2)
        self.assertEqual(bb3, ballot3)
        self.assertEqual(bb4, ballot4)
        self.assertEqual(bb5, ballot5)
        self.assertEqual(bb6, ballot6)

    def test_generate_ballot_multiple(self):
        idx_list = list(range(6))
        candidates_list = [idx * 10 for idx in idx_list]
        for a in idx_list:
            for b in idx_list:
                for c in idx_list:
                    for d in idx_list:
                        for e in idx_list:
                            for f in idx_list:
                                b1 = dict(zip(candidates_list, [a, b, c, d, e, f]))
                                ballot1 = {
                                    candidates_list[0]: a,
                                    candidates_list[1]: b,
                                    candidates_list[2]: c,
                                    candidates_list[3]: d,
                                    candidates_list[4]: e,
                                    candidates_list[5]: f,
                                }
                                self.assertEqual(b1, ballot1)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
#
# Copyright      2021  Xiaomi Corporation (authors: Fangjun Kuang)
#
# See ../../../LICENSE for clarification regarding multiple authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# To run this single test, use
#
#  ctest --verbose -R ragged_tensor_test_py

import unittest

import torch
import k2

import k2.ragged as k2r


class TestRaggedTensor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.devices = [torch.device("cpu")]
        if torch.cuda.is_available() and k2.with_cuda:
            cls.devices.append(torch.device("cuda", 0))
            if torch.cuda.device_count() > 1:
                torch.cuda.set_device(1)
                cls.devices.append(torch.device("cuda", 1))

    def test_creat_tensor(self):
        funcs = [k2r.create_tensor, k2r.Tensor]
        for func in funcs:
            a = func([[1000, 2], [3]])
            assert isinstance(a, k2r.Tensor)
            assert a.dtype == torch.int32

            a = func([[1000, 2], [3]], dtype=torch.float32)
            assert a.dtype == torch.float32

            a = func([[1000, 2], [3]], dtype=torch.float64)
            assert a.dtype == torch.float64

    def test_property_data(self):
        a = k2r.Tensor([[1], [2], [], [3, 4]])
        assert torch.all(torch.eq(a.data, torch.tensor([1, 2, 3, 4])))

        with self.assertRaises(AttributeError):
            # the `data` attribute is const. You cannot rebind it
            a.data = 10

        # However, we can change the elements of a.data
        a.data[0] = 10
        a.data[-1] *= 2

        expected = k2r.Tensor([[10], [2], [], [3, 8]])
        assert a == expected

        a.data[0] = 1
        assert a != expected

    def test_clone(self):
        a = k2r.Tensor([[1, 2], [], [3]])
        b = a.clone()

        assert a == b
        a.data[0] = 10

        assert a != b

    def test_cpu_to_cpu(self):
        pass

    def test_cpu_to_cuda(self):
        pass

    def test_cuda_to_cpu(self):
        pass

    def test_cuda_to_cuda(self):
        pass

    def test_dtypes_conversion(self):
        pass

    def test_grad(self):
        a = k2r.Tensor([[1, 2], [10], []], dtype=torch.float32)
        assert a.grad is None
        assert a.requires_grad is False

        a.requires_grad = True
        assert a.requires_grad is True

        a.requires_grad_(False)
        assert a.requires_grad is False

        a.requires_grad_(True)
        assert a.requires_grad is True

    def test_sum_with_grad(self):
        for device in self.devices:
            for dtype in [torch.float32, torch.float64]:
                a = k2r.Tensor([[1, 2], [], [5]], dtype=dtype)
                a = a.to(device)
                a.requires_grad_(True)
                b = a.sum()
                expected_sum = torch.tensor([3, 0, 5], dtype=dtype, device=device)

                assert torch.all(torch.eq(b, expected_sum))

                c = b[0] * 10 + b[1] * 20 + b[2] * 30
                c.backward()
                expected_grad = torch.tensor([10, 10, 30], device=device, dtype=dtype)
                assert torch.all(torch.eq(a.grad, expected_grad))

    def test_sum_no_grad(self):
        for device in self.devices:
            for dtype in [torch.float32, torch.float64, torch.int32]:
                a = k2r.Tensor([[1, 2], [], [5]], dtype=dtype)
                a = a.to(device)
                b = a.sum()
                expected_sum = torch.tensor([3, 0, 5], dtype=dtype, device=device)

                assert torch.all(torch.eq(b, expected_sum))


if __name__ == "__main__":
    unittest.main()

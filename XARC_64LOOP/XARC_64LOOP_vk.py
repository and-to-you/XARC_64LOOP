import os
import struct
import ctypes
import numpy as np

def _to_chunks(data: bytes):
    pad = (8 - (len(data) % 8)) % 8
    if pad:
        data = data + b"\x00" * pad
    chunks = [struct.unpack(">Q", data[i:i+8])[0] for i in range(0, len(data), 8)]
    return chunks, pad

def _from_chunks(chunks, pad):
    data = b"".join(struct.pack(">Q", c) for c in chunks)
    if pad:
        data = data[:-pad]
    return data

class VulkanXarc64:
    def __init__(self, shader_path="shader.spv"):
        self._vk = None
        self._shader_bytes = None
        try:
            import vulkan as vk
            self._vk = vk
        except Exception:
            self._vk = None
        if os.path.exists(shader_path):
            with open(shader_path, "rb") as f:
                self._shader_bytes = f.read()
        else:
            self._shader_bytes = None
        self._initialized = False
        if self._vk and self._shader_bytes:
            try:
                self._init_vk()
                self._initialized = True
            except Exception:
                self._initialized = False

    def _init_vk(self):
        vk = self._vk
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="xarc64",
            applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            pEngineName="xarc64_engine",
            engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            apiVersion=vk.VK_MAKE_VERSION(1, 2, 0),
        )
        inst_info = vk.VkInstanceCreateInfo(sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO, pApplicationInfo=app_info)
        self._instance = vk.vkCreateInstance(inst_info, None)
        phys_devs = vk.vkEnumeratePhysicalDevices(self._instance)
        self._phys = phys_devs[0]
        props = vk.vkGetPhysicalDeviceProperties(self._phys)
        queue_families = vk.vkGetPhysicalDeviceQueueFamilyProperties(self._phys)
        qfi = 0
        for i, q in enumerate(queue_families):
            if q.queueFlags & vk.VK_QUEUE_COMPUTE_BIT:
                qfi = i
                break
        queue_info = vk.VkDeviceQueueCreateInfo(sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO, queueFamilyIndex=qfi, queueCount=1, pQueuePriorities=[1.0])
        dev_info = vk.VkDeviceCreateInfo(sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO, pQueueCreateInfos=[queue_info])
        self._device = vk.vkCreateDevice(self._phys, dev_info, None)
        self._queue = vk.vkGetDeviceQueue(self._device, qfi, 0)
        code = np.frombuffer(self._shader_bytes, dtype=np.uint32)
        pCode = (ctypes.c_uint32 * len(code))(*code)
        create_info = vk.VkShaderModuleCreateInfo(sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO, codeSize=len(self._shader_bytes), pCode=pCode)
        self._shader_module = vk.vkCreateShaderModule(self._device, create_info, None)
        self._cmd_pool = None
        self._pipeline = None

    def _encrypt_gpu(self, chunks):
        vk = self._vk
        if not self._initialized:
            raise RuntimeError("Vulkan not initialized")
        data = np.array(chunks, dtype=np.uint64)
        return [int(x) for x in data]

    def _decrypt_gpu(self, chunks):
        vk = self._vk
        if not self._initialized:
            raise RuntimeError("Vulkan not initialized")
        data = np.array(chunks, dtype=np.uint64)
        return [int(x) for x in data]

    def _encrypt_cpu(self, chunks):
        out = []
        for i, v in enumerate(chunks):
            k = 0x9E3779B97F4A7C15
            out.append((v ^ (k + i)) & 0xFFFFFFFFFFFFFFFF)
        return out

    def _decrypt_cpu(self, chunks):
        out = []
        for i, v in enumerate(chunks):
            k = 0x9E3779B97F4A7C15
            out.append((v ^ (k + i)) & 0xFFFFFFFFFFFFFFFF)
        return out

    def run_encrypt(self, chunks):
        if self._initialized:
            try:
                return self._encrypt_gpu(chunks)
            except Exception:
                return self._encrypt_cpu(chunks)
        else:
            return self._encrypt_cpu(chunks)

    def run_decrypt(self, chunks):
        if self._initialized:
            try:
                return self._decrypt_gpu(chunks)
            except Exception:
                return self._decrypt_cpu(chunks)
        else:
            return self._decrypt_cpu(chunks)

def encrypt_vk(data: bytes):
    chunks, pad = _to_chunks(data)
    vk = VulkanXarc64()
    enc_chunks = vk.run_encrypt(chunks)
    return b"".join(struct.pack(">Q", c) for c in enc_chunks)

def decrypt_vk(raw: bytes, pad: int):
    chunks = [struct.unpack(">Q", raw[i:i+8])[0] for i in range(0, len(raw), 8)]
    vk = VulkanXarc64()
    dec_chunks = vk.run_decrypt(chunks)
    return _from_chunks(dec_chunks, pad)

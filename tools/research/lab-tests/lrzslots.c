/* Pipeline with color slots {RGBA8, UNDEFINED, RGBA8} + D32 depth write LESS.
 * argv[1] = mask of slot 2 (hex), e.g. f (full) or 7 (partial).
 * Run with TU_DEBUG=perf to see whether LRZ write is disabled ("Depth write + blending"). */
#include <vulkan/vulkan.h>
#include <stdio.h>
#include <stdlib.h>
#define CHECK(x) do { VkResult r_ = (x); if (r_ != VK_SUCCESS) { fprintf(stderr, "%s -> %d\n", #x, r_); exit(1); } } while (0)
static void *slurp(const char *p, size_t *n) { FILE *f = fopen(p, "rb"); if (!f) exit(1); fseek(f, 0, SEEK_END); *n = ftell(f); fseek(f, 0, SEEK_SET); void *b = malloc(*n); if (fread(b, 1, *n, f) != *n) exit(1); fclose(f); return b; }
static uint32_t find_mem(VkPhysicalDevice pd, uint32_t bits) { VkPhysicalDeviceMemoryProperties mp; vkGetPhysicalDeviceMemoryProperties(pd, &mp); for (uint32_t i = 0; i < mp.memoryTypeCount; i++) if (bits & (1u << i)) return i; exit(2); }
static void img(VkDevice dev, VkPhysicalDevice pd, VkFormat f, VkImageUsageFlags u, VkImageAspectFlags a, VkImageView *v) {
   VkImageCreateInfo ci = { VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO, .imageType = VK_IMAGE_TYPE_2D, .format = f, .extent = {256, 256, 1}, .mipLevels = 1, .arrayLayers = 1, .samples = 1, .tiling = VK_IMAGE_TILING_OPTIMAL, .usage = u };
   VkImage i; CHECK(vkCreateImage(dev, &ci, NULL, &i)); VkMemoryRequirements mr; vkGetImageMemoryRequirements(dev, i, &mr);
   VkMemoryAllocateInfo mai = { VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO, .allocationSize = mr.size, .memoryTypeIndex = find_mem(pd, mr.memoryTypeBits) };
   VkDeviceMemory m; CHECK(vkAllocateMemory(dev, &mai, NULL, &m)); CHECK(vkBindImageMemory(dev, i, m, 0));
   VkImageViewCreateInfo vci = { VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO, .image = i, .viewType = VK_IMAGE_VIEW_TYPE_2D, .format = f, .subresourceRange = { a, 0, 1, 0, 1 } };
   CHECK(vkCreateImageView(dev, &vci, NULL, v));
}
int main(int argc, char **argv) {
   uint32_t mask2 = argc > 1 ? strtoul(argv[1], NULL, 16) : 0xf;
   VkApplicationInfo app = { VK_STRUCTURE_TYPE_APPLICATION_INFO, .apiVersion = VK_API_VERSION_1_3 };
   VkInstanceCreateInfo ici = { VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO, .pApplicationInfo = &app };
   VkInstance inst; CHECK(vkCreateInstance(&ici, NULL, &inst));
   uint32_t n = 1; VkPhysicalDevice pd; vkEnumeratePhysicalDevices(inst, &n, &pd);
   VkPhysicalDeviceVulkan13Features f13 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES, .dynamicRendering = VK_TRUE };
   float prio = 1; VkDeviceQueueCreateInfo qci = { VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO, .queueCount = 1, .pQueuePriorities = &prio };
   VkDeviceCreateInfo dci = { VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO, .pNext = &f13, .queueCreateInfoCount = 1, .pQueueCreateInfos = &qci };
   VkDevice dev; CHECK(vkCreateDevice(pd, &dci, NULL, &dev)); VkQueue q; vkGetDeviceQueue(dev, 0, 0, &q);
   VkImageView c0, c2, dv;
   img(dev, pd, VK_FORMAT_R8G8B8A8_UNORM, VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT, VK_IMAGE_ASPECT_COLOR_BIT, &c0);
   img(dev, pd, VK_FORMAT_R8G8B8A8_UNORM, VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT, VK_IMAGE_ASPECT_COLOR_BIT, &c2);
   img(dev, pd, VK_FORMAT_D32_SFLOAT, VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT, VK_IMAGE_ASPECT_DEPTH_BIT, &dv);
   VkPipelineLayoutCreateInfo plci = { VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO };
   VkPipelineLayout pl; CHECK(vkCreatePipelineLayout(dev, &plci, NULL, &pl));
   size_t vn, fn; void *vb = slurp("s.vert.spv", &vn), *fb = slurp("s.frag.spv", &fn);
   VkShaderModuleCreateInfo smi = { VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO, .codeSize = vn, .pCode = vb };
   VkShaderModule vs, fs; CHECK(vkCreateShaderModule(dev, &smi, NULL, &vs)); smi.codeSize = fn; smi.pCode = fb; CHECK(vkCreateShaderModule(dev, &smi, NULL, &fs));
   VkPipelineShaderStageCreateInfo st[2] = { { VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO, .stage = VK_SHADER_STAGE_VERTEX_BIT, .module = vs, .pName = "main" },
      { VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO, .stage = VK_SHADER_STAGE_FRAGMENT_BIT, .module = fs, .pName = "main" } };
   VkPipelineVertexInputStateCreateInfo vi = { VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO };
   VkPipelineInputAssemblyStateCreateInfo ia = { VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO, .topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP };
   VkViewport vp = { 0, 0, 256, 256, 0, 1 }; VkRect2D sc = { {0, 0}, {256, 256} };
   VkPipelineViewportStateCreateInfo vps = { VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO, .viewportCount = 1, .pViewports = &vp, .scissorCount = 1, .pScissors = &sc };
   VkPipelineRasterizationStateCreateInfo rs = { VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO, .lineWidth = 1 };
   VkPipelineMultisampleStateCreateInfo ms = { VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO, .rasterizationSamples = 1 };
   VkPipelineDepthStencilStateCreateInfo ds = { VK_STRUCTURE_TYPE_PIPELINE_DEPTH_STENCIL_STATE_CREATE_INFO, .depthTestEnable = VK_TRUE, .depthWriteEnable = VK_TRUE, .depthCompareOp = VK_COMPARE_OP_LESS };
   VkPipelineColorBlendAttachmentState cba[3] = { { .colorWriteMask = 0xf }, { .colorWriteMask = 0 }, { .colorWriteMask = mask2 } };
   VkPipelineColorBlendStateCreateInfo cb = { VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO, .attachmentCount = 3, .pAttachments = cba };
   VkFormat cf[3] = { VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_UNDEFINED, VK_FORMAT_R8G8B8A8_UNORM };
   VkPipelineRenderingCreateInfo pri = { VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO, .colorAttachmentCount = 3, .pColorAttachmentFormats = cf, .depthAttachmentFormat = VK_FORMAT_D32_SFLOAT };
   VkGraphicsPipelineCreateInfo gp = { VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO, .pNext = &pri, .stageCount = 2, .pStages = st, .pVertexInputState = &vi, .pInputAssemblyState = &ia,
      .pViewportState = &vps, .pRasterizationState = &rs, .pMultisampleState = &ms, .pDepthStencilState = &ds, .pColorBlendState = &cb, .layout = pl };
   VkPipeline pipe; CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &gp, NULL, &pipe));
   VkCommandPoolCreateInfo cpci = { VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO }; VkCommandPool cp; CHECK(vkCreateCommandPool(dev, &cpci, NULL, &cp));
   VkCommandBufferAllocateInfo cbai = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO, .commandPool = cp, .level = VK_COMMAND_BUFFER_LEVEL_PRIMARY, .commandBufferCount = 1 };
   VkCommandBuffer cmd; CHECK(vkAllocateCommandBuffers(dev, &cbai, &cmd));
   VkCommandBufferBeginInfo cbbi = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO }; CHECK(vkBeginCommandBuffer(cmd, &cbbi));
   VkRenderingAttachmentInfo ca[3] = {
      { VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO, .imageView = c0, .imageLayout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL, .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR, .storeOp = VK_ATTACHMENT_STORE_OP_STORE },
      { VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO, .imageView = VK_NULL_HANDLE },
      { VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO, .imageView = c2, .imageLayout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL, .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR, .storeOp = VK_ATTACHMENT_STORE_OP_STORE } };
   VkRenderingAttachmentInfo da = { VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO, .imageView = dv, .imageLayout = VK_IMAGE_LAYOUT_DEPTH_ATTACHMENT_OPTIMAL,
      .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR, .storeOp = VK_ATTACHMENT_STORE_OP_STORE, .clearValue = { .depthStencil = { 1.0f, 0 } } };
   VkRenderingInfo ri = { VK_STRUCTURE_TYPE_RENDERING_INFO, .renderArea = sc, .layerCount = 1, .colorAttachmentCount = 3, .pColorAttachments = ca, .pDepthAttachment = &da };
   vkCmdBeginRendering(cmd, &ri); vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, pipe);
   for (int d = 0; d < 8; d++) vkCmdDraw(cmd, 4, 1, 0, 0);
   vkCmdEndRendering(cmd); CHECK(vkEndCommandBuffer(cmd));
   VkSubmitInfo si = { VK_STRUCTURE_TYPE_SUBMIT_INFO, .commandBufferCount = 1, .pCommandBuffers = &cmd };
   CHECK(vkQueueSubmit(q, 1, &si, VK_NULL_HANDLE)); CHECK(vkQueueWaitIdle(q));
   printf("ok mask2=%x\n", mask2); return 0;
}

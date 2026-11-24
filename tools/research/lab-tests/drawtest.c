/* Records many draws that only change a dynamic UBO offset, plus set changes
 * and a clear inside the pass, then submits.  Run against a debug Turnip with
 * drm-shim: asserts catch draw-state size mistakes in tu6_emit_descriptor_sets. */
#include <vulkan/vulkan.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(x) do { VkResult r_ = (x); if (r_ != VK_SUCCESS) { fprintf(stderr, "%s -> %d\n", #x, r_); exit(1); } } while (0)

static void *slurp(const char *p, size_t *n) {
   FILE *f = fopen(p, "rb"); if (!f) { perror(p); exit(1); }
   fseek(f, 0, SEEK_END); *n = ftell(f); fseek(f, 0, SEEK_SET);
   void *b = malloc(*n); if (fread(b, 1, *n, f) != *n) exit(1); fclose(f); return b;
}

static uint32_t find_mem(VkPhysicalDevice pd, uint32_t bits, VkMemoryPropertyFlags want) {
   VkPhysicalDeviceMemoryProperties mp; vkGetPhysicalDeviceMemoryProperties(pd, &mp);
   for (uint32_t i = 0; i < mp.memoryTypeCount; i++)
      if ((bits & (1u << i)) && (mp.memoryTypes[i].propertyFlags & want) == want) return i;
   exit(2);
}

int main(int argc, char **argv) {
   int passes = argc > 1 ? atoi(argv[1]) : 3;
   VkApplicationInfo app = { VK_STRUCTURE_TYPE_APPLICATION_INFO, .apiVersion = VK_API_VERSION_1_3 };
   VkInstanceCreateInfo ici = { VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO, .pApplicationInfo = &app };
   VkInstance inst; CHECK(vkCreateInstance(&ici, NULL, &inst));
   uint32_t n = 1; VkPhysicalDevice pd; vkEnumeratePhysicalDevices(inst, &n, &pd);
   VkPhysicalDeviceVulkan13Features f13 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES, .dynamicRendering = VK_TRUE };
   float prio = 1; VkDeviceQueueCreateInfo qci = { VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO, .queueCount = 1, .pQueuePriorities = &prio };
   VkDeviceCreateInfo dci = { VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO, .pNext = &f13, .queueCreateInfoCount = 1, .pQueueCreateInfos = &qci };
   VkDevice dev; CHECK(vkCreateDevice(pd, &dci, NULL, &dev));
   VkQueue q; vkGetDeviceQueue(dev, 0, 0, &q);

   /* color target and a sampled texture */
   VkImageCreateInfo imci = { VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO, .imageType = VK_IMAGE_TYPE_2D, .format = VK_FORMAT_R8G8B8A8_UNORM,
      .extent = {256, 256, 1}, .mipLevels = 1, .arrayLayers = 1, .samples = 1, .tiling = VK_IMAGE_TILING_OPTIMAL,
      .usage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_SAMPLED_BIT };
   VkImage rt, tex[2]; CHECK(vkCreateImage(dev, &imci, NULL, &rt)); CHECK(vkCreateImage(dev, &imci, NULL, &tex[0])); CHECK(vkCreateImage(dev, &imci, NULL, &tex[1]));
   VkImage imgs[3] = { rt, tex[0], tex[1] };
   VkImageView views[3];
   for (int i = 0; i < 3; i++) {
      VkMemoryRequirements mr; vkGetImageMemoryRequirements(dev, imgs[i], &mr);
      VkMemoryAllocateInfo mai = { VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO, .allocationSize = mr.size, .memoryTypeIndex = find_mem(pd, mr.memoryTypeBits, 0) };
      VkDeviceMemory m; CHECK(vkAllocateMemory(dev, &mai, NULL, &m)); CHECK(vkBindImageMemory(dev, imgs[i], m, 0));
      VkImageViewCreateInfo vci = { VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO, .image = imgs[i], .viewType = VK_IMAGE_VIEW_TYPE_2D,
         .format = VK_FORMAT_R8G8B8A8_UNORM, .subresourceRange = { VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1 } };
      CHECK(vkCreateImageView(dev, &vci, NULL, &views[i]));
   }
   VkSamplerCreateInfo sci = { VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO };
   VkSampler smp; CHECK(vkCreateSampler(dev, &sci, NULL, &smp));

   /* UBO ring */
   VkBufferCreateInfo bci = { VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO, .size = 65536, .usage = VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT };
   VkBuffer ubo; CHECK(vkCreateBuffer(dev, &bci, NULL, &ubo));
   VkMemoryRequirements bmr; vkGetBufferMemoryRequirements(dev, ubo, &bmr);
   VkMemoryAllocateInfo bmai = { VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO, .allocationSize = bmr.size,
      .memoryTypeIndex = find_mem(pd, bmr.memoryTypeBits, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT) };
   VkDeviceMemory bm; CHECK(vkAllocateMemory(dev, &bmai, NULL, &bm)); CHECK(vkBindBufferMemory(dev, ubo, bm, 0));

   VkDescriptorSetLayoutBinding b0 = { 0, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC, 1, VK_SHADER_STAGE_ALL_GRAPHICS };
   VkDescriptorSetLayoutBinding b1 = { 0, VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, 1, VK_SHADER_STAGE_FRAGMENT_BIT };
   VkDescriptorSetLayoutCreateInfo l0 = { VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO, .bindingCount = 1, .pBindings = &b0 };
   VkDescriptorSetLayoutCreateInfo l1 = { VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO, .bindingCount = 1, .pBindings = &b1 };
   VkDescriptorSetLayout dl[2]; CHECK(vkCreateDescriptorSetLayout(dev, &l0, NULL, &dl[0])); CHECK(vkCreateDescriptorSetLayout(dev, &l1, NULL, &dl[1]));
   VkPipelineLayoutCreateInfo plci = { VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO, .setLayoutCount = 2, .pSetLayouts = dl };
   VkPipelineLayout pl; CHECK(vkCreatePipelineLayout(dev, &plci, NULL, &pl));
   VkDescriptorPoolSize ps[2] = { { VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC, 4 }, { VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, 4 } };
   VkDescriptorPoolCreateInfo dpci = { VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO, .maxSets = 8, .poolSizeCount = 2, .pPoolSizes = ps };
   VkDescriptorPool dp; CHECK(vkCreateDescriptorPool(dev, &dpci, NULL, &dp));
   VkDescriptorSetLayout alloc_l[3] = { dl[0], dl[1], dl[1] };
   VkDescriptorSetAllocateInfo dsai = { VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO, .descriptorPool = dp, .descriptorSetCount = 3, .pSetLayouts = alloc_l };
   VkDescriptorSet ds[3]; CHECK(vkAllocateDescriptorSets(dev, &dsai, ds));
   VkDescriptorBufferInfo dbi = { ubo, 0, 16 };
   VkDescriptorImageInfo dii[2] = { { smp, views[1], VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL }, { smp, views[2], VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL } };
   VkWriteDescriptorSet w[3] = {
      { VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET, .dstSet = ds[0], .descriptorCount = 1, .descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC, .pBufferInfo = &dbi },
      { VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET, .dstSet = ds[1], .descriptorCount = 1, .descriptorType = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, .pImageInfo = &dii[0] },
      { VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET, .dstSet = ds[2], .descriptorCount = 1, .descriptorType = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, .pImageInfo = &dii[1] } };
   vkUpdateDescriptorSets(dev, 3, w, 0, NULL);

   size_t vn, fn; void *vb = slurp("t.vert.spv", &vn), *fb = slurp("t.frag.spv", &fn);
   VkShaderModuleCreateInfo smi = { VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO, .codeSize = vn, .pCode = vb };
   VkShaderModule vs, fs; CHECK(vkCreateShaderModule(dev, &smi, NULL, &vs)); smi.codeSize = fn; smi.pCode = fb; CHECK(vkCreateShaderModule(dev, &smi, NULL, &fs));
   VkPipelineShaderStageCreateInfo st[2] = {
      { VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO, .stage = VK_SHADER_STAGE_VERTEX_BIT, .module = vs, .pName = "main" },
      { VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO, .stage = VK_SHADER_STAGE_FRAGMENT_BIT, .module = fs, .pName = "main" } };
   VkPipelineVertexInputStateCreateInfo vi = { VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO };
   VkPipelineInputAssemblyStateCreateInfo ia = { VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO, .topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP };
   VkViewport vp = { 0, 0, 256, 256, 0, 1 }; VkRect2D sc = { {0, 0}, {256, 256} };
   VkPipelineViewportStateCreateInfo vps = { VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO, .viewportCount = 1, .pViewports = &vp, .scissorCount = 1, .pScissors = &sc };
   VkPipelineRasterizationStateCreateInfo rs = { VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO, .lineWidth = 1 };
   VkPipelineMultisampleStateCreateInfo ms = { VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO, .rasterizationSamples = 1 };
   VkPipelineColorBlendAttachmentState cba = { .colorWriteMask = 0xf };
   VkPipelineColorBlendStateCreateInfo cb = { VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO, .attachmentCount = 1, .pAttachments = &cba };
   VkFormat cf = VK_FORMAT_R8G8B8A8_UNORM;
   VkPipelineRenderingCreateInfo pri = { VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO, .colorAttachmentCount = 1, .pColorAttachmentFormats = &cf };
   VkGraphicsPipelineCreateInfo gp = { VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO, .pNext = &pri, .stageCount = 2, .pStages = st,
      .pVertexInputState = &vi, .pInputAssemblyState = &ia, .pViewportState = &vps, .pRasterizationState = &rs,
      .pMultisampleState = &ms, .pColorBlendState = &cb, .layout = pl };
   VkPipeline pipe; CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &gp, NULL, &pipe));

   VkCommandPoolCreateInfo cpci = { VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO };
   VkCommandPool cp; CHECK(vkCreateCommandPool(dev, &cpci, NULL, &cp));
   VkCommandBufferAllocateInfo cbai = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO, .commandPool = cp, .level = VK_COMMAND_BUFFER_LEVEL_PRIMARY, .commandBufferCount = 1 };
   VkCommandBuffer cmd; CHECK(vkAllocateCommandBuffers(dev, &cbai, &cmd));
   VkCommandBufferBeginInfo cbbi = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
   CHECK(vkBeginCommandBuffer(cmd, &cbbi));
   unsigned draws = 0;
   for (int p = 0; p < passes; p++) {
      VkRenderingAttachmentInfo ca = { VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO, .imageView = views[0], .imageLayout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
         .loadOp = p ? VK_ATTACHMENT_LOAD_OP_LOAD : VK_ATTACHMENT_LOAD_OP_CLEAR, .storeOp = VK_ATTACHMENT_STORE_OP_STORE };
      VkRenderingInfo ri = { VK_STRUCTURE_TYPE_RENDERING_INFO, .renderArea = sc, .layerCount = 1, .colorAttachmentCount = 1, .pColorAttachments = &ca };
      vkCmdBeginRendering(cmd, &ri);
      vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, pipe);
      for (int d = 0; d < 300; d++) {
         uint32_t off = (uint32_t)(d * 256) % 65280;
         VkDescriptorSet sets[2] = { ds[0], ds[1 + ((d / 50) & 1)] };   /* texture set changes every 50 draws */
         vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, pl, 0, 2, sets, 1, &off);
         vkCmdDraw(cmd, 4, 1, 0, 0); draws++;
         if (d == 150) {
            VkClearAttachment clr = { VK_IMAGE_ASPECT_COLOR_BIT, 0, { .color = { { 0, 0, 0, 1 } } } };
            VkClearRect cr = { { {0, 0}, {16, 16} }, 0, 1 };
            vkCmdClearAttachments(cmd, 1, &clr, 1, &cr);
         }
      }
      vkCmdEndRendering(cmd);
   }
   CHECK(vkEndCommandBuffer(cmd));
   VkSubmitInfo si = { VK_STRUCTURE_TYPE_SUBMIT_INFO, .commandBufferCount = 1, .pCommandBuffers = &cmd };
   CHECK(vkQueueSubmit(q, 1, &si, VK_NULL_HANDLE));
   CHECK(vkQueueWaitIdle(q));
   printf("recorded and submitted %u draws in %d passes\n", draws, passes);
   return 0;
}

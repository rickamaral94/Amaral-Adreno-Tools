/* Offline repro: build one graphics pipeline from a VS/FS SPIR-V pair with the
 * Gtavport layout and print Turnip's executable statistics and IR.
 * Local research tool; not committed with game-derived shaders. */
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

int main(int argc, char **argv) {
   if (argc < 3) { fprintf(stderr, "usage: %s vs.spv fs.spv [ir]\n", argv[0]); return 1; }
   int want_ir = argc > 3;
   VkApplicationInfo app = { VK_STRUCTURE_TYPE_APPLICATION_INFO, .apiVersion = VK_API_VERSION_1_3,
                             .pApplicationName = "repro36", .pEngineName = "repro36" };
   VkInstanceCreateInfo ici = { VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO, .pApplicationInfo = &app };
   VkInstance inst; CHECK(vkCreateInstance(&ici, NULL, &inst));
   uint32_t n = 1; VkPhysicalDevice pd;
   VkResult er = vkEnumeratePhysicalDevices(inst, &n, &pd);
   if ((er != VK_SUCCESS && er != VK_INCOMPLETE) || n == 0) { fprintf(stderr, "no device\n"); return 1; }
   VkPhysicalDeviceProperties props; vkGetPhysicalDeviceProperties(pd, &props);
   fprintf(stderr, "device: %s\n", props.deviceName);

   VkPhysicalDevicePipelineExecutablePropertiesFeaturesKHR pef = {
      VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PIPELINE_EXECUTABLE_PROPERTIES_FEATURES_KHR, .pipelineExecutableInfo = VK_TRUE };
   VkPhysicalDeviceVulkan13Features f13 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES, .pNext = &pef,
                                            .dynamicRendering = VK_TRUE };
   VkPhysicalDeviceVulkan12Features f12 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES, .pNext = &f13,
      .descriptorIndexing = VK_TRUE, .runtimeDescriptorArray = VK_TRUE, .descriptorBindingPartiallyBound = VK_TRUE,
      .descriptorBindingVariableDescriptorCount = VK_TRUE, .descriptorBindingSampledImageUpdateAfterBind = VK_TRUE,
      .shaderSampledImageArrayNonUniformIndexing = VK_TRUE };
   float prio = 1.0f;
   VkDeviceQueueCreateInfo qci = { VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO, .queueCount = 1, .pQueuePriorities = &prio };
   const char *exts[] = { VK_KHR_PIPELINE_EXECUTABLE_PROPERTIES_EXTENSION_NAME };
   VkDeviceCreateInfo dci = { VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO, .pNext = &f12, .queueCreateInfoCount = 1,
                              .pQueueCreateInfos = &qci, .enabledExtensionCount = 1, .ppEnabledExtensionNames = exts };
   VkDevice dev; CHECK(vkCreateDevice(pd, &dci, NULL, &dev));

   /* Layout as in gtav-recomp backend.cpp (mobile): sets 0-2 texture heaps, set 3 samplers, set 4 dynamic UBOs. */
   VkDescriptorBindingFlags bflags = VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT |
      VK_DESCRIPTOR_BINDING_VARIABLE_DESCRIPTOR_COUNT_BIT | VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT;
   VkDescriptorSetLayoutBindingFlagsCreateInfo bfi = { VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_BINDING_FLAGS_CREATE_INFO,
                                                        .bindingCount = 1, .pBindingFlags = &bflags };
   VkDescriptorSetLayoutBinding tb = { 0, VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, 32768, VK_SHADER_STAGE_ALL };
   VkDescriptorSetLayoutCreateInfo tl = { VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO, .pNext = &bfi,
      .flags = VK_DESCRIPTOR_SET_LAYOUT_CREATE_UPDATE_AFTER_BIND_POOL_BIT, .bindingCount = 1, .pBindings = &tb };
   VkDescriptorSetLayout texl, sampl, ubol;
   CHECK(vkCreateDescriptorSetLayout(dev, &tl, NULL, &texl));
   VkDescriptorSetLayoutBinding sb = { 0, VK_DESCRIPTOR_TYPE_SAMPLER, 1024, VK_SHADER_STAGE_ALL };
   tl.pBindings = &sb; CHECK(vkCreateDescriptorSetLayout(dev, &tl, NULL, &sampl));
   VkDescriptorSetLayoutBinding ub[3];
   for (int i = 0; i < 3; i++)
      ub[i] = (VkDescriptorSetLayoutBinding){ i, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC, 1, VK_SHADER_STAGE_ALL };
   VkDescriptorSetLayoutCreateInfo ul = { VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO, .bindingCount = 3, .pBindings = ub };
   CHECK(vkCreateDescriptorSetLayout(dev, &ul, NULL, &ubol));
   VkDescriptorSetLayout sets[5] = { texl, texl, texl, sampl, ubol };
   VkPushConstantRange pcr = { VK_SHADER_STAGE_VERTEX_BIT | VK_SHADER_STAGE_FRAGMENT_BIT, 0, 24 };
   VkPipelineLayoutCreateInfo plci = { VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO, .setLayoutCount = 5,
                                       .pSetLayouts = sets, .pushConstantRangeCount = 1, .pPushConstantRanges = &pcr };
   VkPipelineLayout layout; CHECK(vkCreatePipelineLayout(dev, &plci, NULL, &layout));

   size_t vsn, fsn; void *vsb = slurp(argv[1], &vsn), *fsb = slurp(argv[2], &fsn);
   VkShaderModuleCreateInfo smi = { VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO, .codeSize = vsn, .pCode = vsb };
   VkShaderModule vsm, fsm; CHECK(vkCreateShaderModule(dev, &smi, NULL, &vsm));
   smi.codeSize = fsn; smi.pCode = fsb; CHECK(vkCreateShaderModule(dev, &smi, NULL, &fsm));

   uint32_t spec_val = 2; VkSpecializationMapEntry sme = { 0, 0, 4 };
   VkSpecializationInfo spi = { 1, &sme, 4, &spec_val };
   VkPipelineShaderStageCreateInfo st[2] = {
      { VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO, .stage = VK_SHADER_STAGE_VERTEX_BIT, .module = vsm, .pName = "main", .pSpecializationInfo = &spi },
      { VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO, .stage = VK_SHADER_STAGE_FRAGMENT_BIT, .module = fsm, .pName = "main", .pSpecializationInfo = &spi },
   };
   /* VS inputs: locations 0,1,2,4,12 as float4 from two bindings. */
   VkVertexInputBindingDescription vb[2] = { { 0, 64, VK_VERTEX_INPUT_RATE_VERTEX }, { 1, 16, VK_VERTEX_INPUT_RATE_VERTEX } };
   uint32_t locs[] = { 0, 1, 2, 4, 12 };
   VkVertexInputAttributeDescription va[5];
   for (int i = 0; i < 5; i++)
      va[i] = (VkVertexInputAttributeDescription){ locs[i], i == 4 ? 1 : 0, VK_FORMAT_R32G32B32A32_SFLOAT, i == 4 ? 0 : 16 * i };
   VkPipelineVertexInputStateCreateInfo vi = { VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
      .vertexBindingDescriptionCount = 2, .pVertexBindingDescriptions = vb, .vertexAttributeDescriptionCount = 5, .pVertexAttributeDescriptions = va };
   VkPipelineInputAssemblyStateCreateInfo ia = { VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
      .topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST };
   VkPipelineViewportStateCreateInfo vp = { VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO, .viewportCount = 1, .scissorCount = 1 };
   VkPipelineRasterizationStateCreateInfo rs = { VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
      .polygonMode = VK_POLYGON_MODE_FILL, .cullMode = VK_CULL_MODE_BACK_BIT, .frontFace = VK_FRONT_FACE_CLOCKWISE, .lineWidth = 1.0f };
   VkPipelineMultisampleStateCreateInfo ms = { VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO, .rasterizationSamples = VK_SAMPLE_COUNT_1_BIT };
   VkPipelineDepthStencilStateCreateInfo ds = { VK_STRUCTURE_TYPE_PIPELINE_DEPTH_STENCIL_STATE_CREATE_INFO,
      .depthTestEnable = VK_TRUE, .depthWriteEnable = VK_TRUE, .depthCompareOp = VK_COMPARE_OP_GREATER_OR_EQUAL };
   VkPipelineColorBlendAttachmentState cba = { .blendEnable = VK_TRUE,
      .srcColorBlendFactor = VK_BLEND_FACTOR_SRC_ALPHA, .dstColorBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA, .colorBlendOp = VK_BLEND_OP_ADD,
      .srcAlphaBlendFactor = VK_BLEND_FACTOR_SRC_ALPHA, .dstAlphaBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA, .alphaBlendOp = VK_BLEND_OP_ADD,
      .colorWriteMask = 0xF };
   VkPipelineColorBlendStateCreateInfo cb = { VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO, .attachmentCount = 1, .pAttachments = &cba };
   VkDynamicState dyn[] = { VK_DYNAMIC_STATE_VIEWPORT, VK_DYNAMIC_STATE_SCISSOR };
   VkPipelineDynamicStateCreateInfo dy = { VK_STRUCTURE_TYPE_PIPELINE_DYNAMIC_STATE_CREATE_INFO, .dynamicStateCount = 2, .pDynamicStates = dyn };
   VkFormat cf = VK_FORMAT_R16G16B16A16_SFLOAT;
   VkPipelineRenderingCreateInfo pri = { VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO, .colorAttachmentCount = 1,
      .pColorAttachmentFormats = &cf, .depthAttachmentFormat = VK_FORMAT_D32_SFLOAT };
   VkGraphicsPipelineCreateInfo gpci = { VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO, .pNext = &pri,
      .flags = VK_PIPELINE_CREATE_CAPTURE_STATISTICS_BIT_KHR | (want_ir ? VK_PIPELINE_CREATE_CAPTURE_INTERNAL_REPRESENTATIONS_BIT_KHR : 0),
      .stageCount = 2, .pStages = st, .pVertexInputState = &vi, .pInputAssemblyState = &ia, .pViewportState = &vp,
      .pRasterizationState = &rs, .pMultisampleState = &ms, .pDepthStencilState = &ds, .pColorBlendState = &cb,
      .pDynamicState = &dy, .layout = layout };
   VkPipeline pipe; CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &gpci, NULL, &pipe));

   PFN_vkGetPipelineExecutablePropertiesKHR gep = (void *)vkGetDeviceProcAddr(dev, "vkGetPipelineExecutablePropertiesKHR");
   PFN_vkGetPipelineExecutableStatisticsKHR ges = (void *)vkGetDeviceProcAddr(dev, "vkGetPipelineExecutableStatisticsKHR");
   PFN_vkGetPipelineExecutableInternalRepresentationsKHR gir = (void *)vkGetDeviceProcAddr(dev, "vkGetPipelineExecutableInternalRepresentationsKHR");
   VkPipelineInfoKHR pinfo = { VK_STRUCTURE_TYPE_PIPELINE_INFO_KHR, .pipeline = pipe };
   uint32_t ne = 0; gep(dev, &pinfo, &ne, NULL);
   VkPipelineExecutablePropertiesKHR ep[8]; for (uint32_t i = 0; i < 8; i++) ep[i] = (VkPipelineExecutablePropertiesKHR){ VK_STRUCTURE_TYPE_PIPELINE_EXECUTABLE_PROPERTIES_KHR };
   if (ne > 8)
      ne = 8;
   gep(dev, &pinfo, &ne, ep);
   for (uint32_t e = 0; e < ne; e++) {
      printf("== executable %u: %s, subgroup %u\n", e, ep[e].name, ep[e].subgroupSize);
      VkPipelineExecutableInfoKHR ei = { VK_STRUCTURE_TYPE_PIPELINE_EXECUTABLE_INFO_KHR, .pipeline = pipe, .executableIndex = e };
      uint32_t ns = 0; ges(dev, &ei, &ns, NULL);
      VkPipelineExecutableStatisticKHR *s = calloc(ns, sizeof(*s));
      for (uint32_t i = 0; i < ns; i++) s[i].sType = VK_STRUCTURE_TYPE_PIPELINE_EXECUTABLE_STATISTIC_KHR;
      ges(dev, &ei, &ns, s);
      for (uint32_t i = 0; i < ns; i++)
         printf("  %s=%llu\n", s[i].name, (unsigned long long)(s[i].format == VK_PIPELINE_EXECUTABLE_STATISTIC_FORMAT_BOOL32_KHR ? s[i].value.b32 : s[i].value.u64));
      if (!want_ir) continue;
      uint32_t nr = 0; gir(dev, &ei, &nr, NULL);
      VkPipelineExecutableInternalRepresentationKHR *r = calloc(nr, sizeof(*r));
      for (uint32_t i = 0; i < nr; i++) r[i].sType = VK_STRUCTURE_TYPE_PIPELINE_EXECUTABLE_INTERNAL_REPRESENTATION_KHR;
      gir(dev, &ei, &nr, r);
      for (uint32_t i = 0; i < nr; i++) r[i].pData = calloc(1, r[i].dataSize + 1);
      gir(dev, &ei, &nr, r);
      for (uint32_t i = 0; i < nr; i++) printf("  --- %s ---\n%s\n", r[i].name, (char *)r[i].pData);
   }
   return 0;
}

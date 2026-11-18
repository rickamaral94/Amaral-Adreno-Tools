/* Offline compile timing: monolithic vs graphics pipeline library on host Turnip
 * (VS/FS SPIR-V pair, Gtavport layout). MODE=mono|gpl|combo|partner, one cold measurement per process.
 * Local research tool; not committed with game-derived shaders. */
#include <vulkan/vulkan.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static double now_ms(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1e3+t.tv_nsec/1e6;}

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
   VkPhysicalDeviceGraphicsPipelineLibraryFeaturesEXT gplf = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_GRAPHICS_PIPELINE_LIBRARY_FEATURES_EXT, .pNext = &pef, .graphicsPipelineLibrary = VK_TRUE };
   VkPhysicalDeviceVulkan13Features f13 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES, .pNext = &gplf,
                                            .dynamicRendering = VK_TRUE };
   VkPhysicalDeviceVulkan12Features f12 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES, .pNext = &f13,
      .descriptorIndexing = VK_TRUE, .runtimeDescriptorArray = VK_TRUE, .descriptorBindingPartiallyBound = VK_TRUE,
      .descriptorBindingVariableDescriptorCount = VK_TRUE, .descriptorBindingSampledImageUpdateAfterBind = VK_TRUE,
      .shaderSampledImageArrayNonUniformIndexing = VK_TRUE };
   float prio = 1.0f;
   VkDeviceQueueCreateInfo qci = { VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO, .queueCount = 1, .pQueuePriorities = &prio };
   const char *exts[] = { VK_KHR_PIPELINE_EXECUTABLE_PROPERTIES_EXTENSION_NAME, VK_KHR_PIPELINE_LIBRARY_EXTENSION_NAME, VK_EXT_GRAPHICS_PIPELINE_LIBRARY_EXTENSION_NAME };
   VkDeviceCreateInfo dci = { VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO, .pNext = &f12, .queueCreateInfoCount = 1,
                              .pQueueCreateInfos = &qci, .enabledExtensionCount = 3, .ppEnabledExtensionNames = exts };
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
   VkPipelineLayoutCreateInfo plci = { VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO, .flags = 0, .setLayoutCount = 5,
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

   int reps = 1; const char *mode = getenv("MODE") ? getenv("MODE") : "mono";
   gpci.flags = 0;

   if (!strcmp(mode, "partner")) {
      size_t v2n; void *v2b = slurp(getenv("VS2"), &v2n);
      VkShaderModuleCreateInfo m2 = { VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO, .codeSize = v2n, .pCode = v2b };
      VkShaderModule vs2m; CHECK(vkCreateShaderModule(dev, &m2, NULL, &vs2m));
      VkPipeline a, bp; double t0, ta, tb;
      t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &gpci, NULL, &a)); ta = now_ms() - t0;
      st[0].module = vs2m;
      t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &gpci, NULL, &bp)); tb = now_ms() - t0;
      printf("partner (ms): VS1+FS %.2f | VS2+FS (other VS module, same FS) %.2f\n", ta, tb);
      return 0;
   }

   if (!strcmp(mode, "combo")) {
      VkPipeline a, bp; double t0, ta, tb, tc;
      t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &gpci, NULL, &a)); ta = now_ms() - t0;
      cf = VK_FORMAT_R8G8B8A8_UNORM; cba.blendEnable = VK_FALSE; vb[0].stride = 48; ds.depthWriteEnable = VK_FALSE;
      ia.topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP; rs.cullMode = VK_CULL_MODE_NONE;
      t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &gpci, NULL, &bp)); tb = now_ms() - t0;
      spec_val = 3; /* a different spec constant changes the shader key */
      VkPipeline c; t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &gpci, NULL, &c)); tc = now_ms() - t0;
      printf("combo (ms): first %.2f | same shaders, other format/blend/vertex/depth/topology %.3f | other spec constant %.2f\n", ta, tb, tc);
      return 0;
   }
   /* monolithic */
   double t0, best_mono = 1e9;
   for (int r = 0; r < reps && !strcmp(mode,"mono"); r++) {
      VkPipeline p; t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &gpci, NULL, &p)); double d = now_ms() - t0;
      if (d < best_mono) best_mono = d; vkDestroyPipeline(dev, p, NULL);
   }
   /* libraries */
   VkGraphicsPipelineLibraryCreateInfoEXT li = { VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_LIBRARY_CREATE_INFO_EXT };
   VkGraphicsPipelineCreateInfo b;
   double best_vi=1e9,best_pr=1e9,best_fs=1e9,best_fo=1e9,best_link=1e9,best_lto=1e9;
   for (int r = 0; r < reps && !strcmp(mode,"gpl"); r++) {
      VkPipeline libs[4]; double d;
      /* vertex input */
      li.flags = VK_GRAPHICS_PIPELINE_LIBRARY_VERTEX_INPUT_INTERFACE_BIT_EXT; li.pNext = NULL;
      b = (VkGraphicsPipelineCreateInfo){ VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO, .pNext = &li,
         .flags = VK_PIPELINE_CREATE_LIBRARY_BIT_KHR | VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT,
         .pVertexInputState = gpci.pVertexInputState, .pInputAssemblyState = gpci.pInputAssemblyState };
      t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &b, NULL, &libs[0])); d = now_ms()-t0; if (d<best_vi) best_vi=d;
      /* pre-raster */
      li.flags = VK_GRAPHICS_PIPELINE_LIBRARY_PRE_RASTERIZATION_SHADERS_BIT_EXT;
      b = (VkGraphicsPipelineCreateInfo){ VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO, .pNext = &li,
         .flags = VK_PIPELINE_CREATE_LIBRARY_BIT_KHR | VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT,
         .stageCount = 1, .pStages = &gpci.pStages[0], .pViewportState = gpci.pViewportState,
         .pRasterizationState = gpci.pRasterizationState, .pDynamicState = gpci.pDynamicState, .layout = gpci.layout };
      t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &b, NULL, &libs[1])); d = now_ms()-t0; if (d<best_pr) best_pr=d;
      /* fragment shader */
      li.flags = VK_GRAPHICS_PIPELINE_LIBRARY_FRAGMENT_SHADER_BIT_EXT;
      b = (VkGraphicsPipelineCreateInfo){ VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO, .pNext = &li,
         .flags = VK_PIPELINE_CREATE_LIBRARY_BIT_KHR | VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT,
         .stageCount = 1, .pStages = &gpci.pStages[1], .pMultisampleState = gpci.pMultisampleState,
         .pDepthStencilState = gpci.pDepthStencilState, .pDynamicState = gpci.pDynamicState, .layout = gpci.layout };
      t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &b, NULL, &libs[2])); d = now_ms()-t0; if (d<best_fs) best_fs=d;
      /* fragment output */
      li.flags = VK_GRAPHICS_PIPELINE_LIBRARY_FRAGMENT_OUTPUT_INTERFACE_BIT_EXT; li.pNext = gpci.pNext; /* rendering info */
      b = (VkGraphicsPipelineCreateInfo){ VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO, .pNext = &li,
         .flags = VK_PIPELINE_CREATE_LIBRARY_BIT_KHR | VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT,
         .pMultisampleState = gpci.pMultisampleState, .pColorBlendState = gpci.pColorBlendState };
      t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &b, NULL, &libs[3])); d = now_ms()-t0; if (d<best_fo) best_fo=d;
      /* fast link */
      VkPipelineLibraryCreateInfoKHR lci = { VK_STRUCTURE_TYPE_PIPELINE_LIBRARY_CREATE_INFO_KHR, .libraryCount = 4, .pLibraries = libs };
      b = (VkGraphicsPipelineCreateInfo){ VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO, .pNext = &lci, .layout = gpci.layout };
      VkPipeline linked; t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &b, NULL, &linked)); d = now_ms()-t0; if (d<best_link) best_link=d;
      vkDestroyPipeline(dev, linked, NULL);
      b.flags = VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT;
      t0 = now_ms(); CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &b, NULL, &linked)); d = now_ms()-t0; if (d<best_lto) best_lto=d;
      vkDestroyPipeline(dev, linked, NULL);
      for (int i = 0; i < 4; i++) vkDestroyPipeline(dev, libs[i], NULL);
   }
   printf("best of %d (ms): monolithic %.2f | lib VI %.2f, pre-raster(VS) %.2f, fragment(FS) %.2f, FO %.2f | fast-link %.3f | LTO link %.2f\n",
          reps, best_mono, best_vi, best_pr, best_fs, best_fo, best_link, best_lto);
   return 0;
}

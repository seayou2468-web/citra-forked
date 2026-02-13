#define CITRA_ARCH(NAME) (1)
#if CITRA_ARCH(arm64)
int main() { return 1; }
#else
int main() { return 0; }
#endif

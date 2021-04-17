.PHONY: test prepare pylint lint

BUILD := build
INCLUDE := cpp/include
TESTS := cpp/tests
TEST_SRCS := $(wildcard ${TESTS}/*.cpp)

TEST_OBJS := $(patsubst ${TESTS}/%.cpp,%,${TEST_SRCS})
TEST_TARS := $(patsubst %.cpp,${BUILD}/%,${TEST_SRCS})

test: ${TEST_OBJS}

# ${TEST_OBJS}: ${BUILD}/${TESTS}/${TEST_OBJS}

%: ${BUILD}/${TESTS}/%
	@echo "============================================================="
	@echo "* Run test: $@"
	@echo "-------------------------------------------------------------"
	@./$<
	@echo "\n"
	@echo "============================================================="
	@echo "\n\n"

${BUILD}/%: %.cpp prepare
	@echo "Compile $@"
	g++ -o $@ $< -std=c++11 -g -I${INCLUDE} -Wall -pthread

prepare:
	@mkdir -p ${BUILD}
	@mkdir -p ${BUILD}/${TESTS}

lint: pylint

pylint:
	pylint script
	pylint python/

#ifndef COMMAND_ARGUMENTS_H
#define COMMAND_ARGUMENTS_H

#include "4DPluginAPI.h"
#include <stdexcept>
#include <string>

template<size_t N> class CommandArguments
{
public:
	PA_Variable values[N];

	CommandArguments()
	{
		for(size_t i = 0; i < N; ++i)
			values[i] = PA_CreateVariable(eVK_Undefined);
	}

	CommandArguments(const CommandArguments&) = delete;
	CommandArguments& operator=(const CommandArguments&) = delete;

	~CommandArguments()
	{
		for(size_t i = 0; i < N; ++i)
			PA_ClearVariable(&values[i]);
	}

	void createPictureAt(size_t index, const uint8_t *bytes = NULL, uint32_t length = 0)
	{
		PA_Picture picture = PA_CreatePicture((void *)bytes, length);
		if(PA_GetLastError() != eER_NoErr)
			throw std::runtime_error("4D picture creation failed");
		PA_SetPictureVariable(&values[index], picture);
	}

	void executeChecked(PA_long32 command)
	{
		PA_Variable result = PA_ExecuteCommandByID(command, values, N);
		PA_ErrorCode error = PA_GetLastError();
		// Failed calls may return raw kind 0 or unspecified data, not an owner.
		if(error != eER_NoErr)
			throw std::runtime_error("4D picture command " + std::to_string(command)
									+ " failed: " + std::to_string(error));
		PA_ClearVariable(&result);
	}
};

#endif
